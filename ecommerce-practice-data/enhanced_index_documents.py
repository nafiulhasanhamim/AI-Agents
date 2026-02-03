import json
import os
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader

@dataclass
class ChunkConfig:
    chunk_size: int
    chunk_overlap: int
    content_type: str

# Different chunking strategies for different content types
CHUNK_CONFIGS = {
    "product_summary": ChunkConfig(400, 50, "product"),
    "product_section": ChunkConfig(800, 100, "product"),
    "policy": ChunkConfig(1500, 200, "policy"),
    "faq": ChunkConfig(1200, 150, "faq"),
    "review": ChunkConfig(600, 75, "review")
}

class HybridChunker:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
    def create_product_chunks(self, product: Dict[str, Any]) -> List[Document]:
        """Create hybrid chunks for a single product"""
        chunks = []
        base_metadata = {
            "content_type": "product",
            "product_id": product["id"],
            "product_name": product["name"],
            "category": product["category"],
            "subcategory": product.get("subcategory", ""),
            "brand": product["brand"],
            "price": product["price"],
            "currency": product["currency"],
            "in_stock": product["in_stock"],
            "on_sale": product.get("on_sale", False),
            "rating": product.get("reviews", {}).get("average_rating", 0),
            "review_count": product.get("reviews", {}).get("total_reviews", 0),
            "last_updated": product["last_updated"]
        }
        
        # 1. Canonical Summary Chunk (ALWAYS CREATED - HIGHEST PRIORITY)
        summary_text = self._create_canonical_summary(product)
        chunks.append(Document(
            page_content=summary_text,
            metadata={
                **base_metadata,
                "chunk_type": "summary",
                "boost_score": 1.3,  # Higher boost for summary chunks
                "section": "summary"
            }
        ))
        
        # 2. Specifications Chunk
        if product.get("specifications"):
            specs_text = self._format_specifications(product["specifications"])
            chunks.append(Document(
                page_content=specs_text,
                metadata={
                    **base_metadata,
                    "chunk_type": "section",
                    "section": "specifications",
                    "boost_score": 1.1
                }
            ))
        
        # 3. Features Chunk
        if product.get("features"):
            features_text = "Key Features:\n" + "\n".join([f"• {feature}" for feature in product["features"]])
            chunks.append(Document(
                page_content=features_text,
                metadata={
                    **base_metadata,
                    "chunk_type": "section",
                    "section": "features",
                    "boost_score": 1.1
                }
            ))
        
        # 4. Detailed Description Chunks (split if long)
        if product.get("detailed_description"):
            desc_chunks = self._split_long_content(
                product["detailed_description"],
                CHUNK_CONFIGS["product_section"],
                base_metadata,
                "description"
            )
            chunks.extend(desc_chunks)
        
        # 5. Reviews Summary Chunk
        if product.get("reviews") and product["reviews"].get("total_reviews", 0) > 0:
            review_summary = self._create_review_summary(product["reviews"])
            chunks.append(Document(
                page_content=review_summary,
                metadata={
                    **base_metadata,
                    "chunk_type": "section",
                    "section": "reviews",
                    "boost_score": 1.0
                }
            ))
        
        # 6. Warranty and Support Chunk
        if product.get("warranty"):
            warranty_text = self._format_warranty_info(product["warranty"])
            chunks.append(Document(
                page_content=warranty_text,
                metadata={
                    **base_metadata,
                    "chunk_type": "section",
                    "section": "warranty",
                    "boost_score": 0.9
                }
            ))
        
        return chunks
    
    def _create_canonical_summary(self, product: Dict[str, Any]) -> str:
        """Create a concise, consistent summary for every product"""
        summary_parts = [
            f"Product: {product['name']}",
            f"Brand: {product['brand']}",
            f"Category: {product['category']}",
            f"Price: ${product['price']} {product['currency']}",
        ]
        
        if product.get("short_description"):
            summary_parts.append(f"Description: {product['short_description']}")
        
        # Stock status
        if product.get("in_stock"):
            if product.get("stock_quantity", 0) > 0:
                summary_parts.append(f"Status: In Stock ({product['stock_quantity']} available)")
            else:
                summary_parts.append("Status: In Stock")
        else:
            summary_parts.append("Status: Out of Stock")
            
        # Sale information
        if product.get("on_sale"):
            summary_parts.append(f"On Sale: {product.get('discount_percent', 0)}% off (was ${product.get('original_price', product['price'])})")
        
        # Rating information
        if product.get("reviews", {}).get("average_rating"):
            rating = product["reviews"]["average_rating"]
            count = product["reviews"]["total_reviews"]
            summary_parts.append(f"Rating: {rating}/5 stars ({count} reviews)")
        
        # Key specifications (category-specific)
        key_specs = self._extract_key_specifications(product)
        if key_specs:
            summary_parts.append(f"Key Specs: {key_specs}")
        
        return ". ".join(summary_parts) + "."
    
    def _extract_key_specifications(self, product: Dict[str, Any]) -> str:
        """Extract key specifications for summary"""
        specs = product.get("specifications", {})
        category = product.get("category", "")
        
        if "Gaming Laptops" in category:
            key_parts = []
            if "processor" in specs:
                key_parts.append(specs["processor"].get("model", ""))
            if "graphics" in specs:
                key_parts.append(specs["graphics"].get("model", ""))
            if "memory" in specs:
                key_parts.append(specs["memory"].get("capacity", ""))
            return ", ".join([part for part in key_parts if part])
        
        elif "Smartphones" in category:
            key_parts = []
            if "processor" in specs:
                key_parts.append(specs["processor"].get("chipset", ""))
            if "camera" in specs and "main" in specs["camera"]:
                key_parts.append(specs["camera"]["main"].get("sensor", ""))
            if "battery" in specs:
                key_parts.append(specs["battery"].get("capacity", ""))
            return ", ".join([part for part in key_parts if part])
        
        elif "Headphones" in category:
            key_parts = []
            if "audio" in specs:
                key_parts.append(f"{specs['audio'].get('driver_size', '')} drivers")
            if "connectivity" in specs:
                key_parts.append(specs["connectivity"].get("wireless", ""))
            if "battery" in specs:
                key_parts.append(specs["battery"].get("life", ""))
            return ", ".join([part for part in key_parts if part])
        
        return ""
    
    def _format_specifications(self, specs: Dict[str, Any]) -> str:
        """Format specifications into readable text"""
        spec_lines = ["Technical Specifications:"]
        
        def format_spec_section(section_name: str, section_data: Any, indent: int = 0):
            lines = []
            prefix = "  " * indent
            
            if isinstance(section_data, dict):
                lines.append(f"{prefix}{section_name.replace('_', ' ').title()}:")
                for key, value in section_data.items():
                    if isinstance(value, dict):
                        lines.extend(format_spec_section(key, value, indent + 1))
                    elif isinstance(value, list):
                        lines.append(f"{prefix}  {key.replace('_', ' ').title()}: {', '.join(map(str, value))}")
                    else:
                        lines.append(f"{prefix}  {key.replace('_', ' ').title()}: {value}")
            else:
                lines.append(f"{prefix}{section_name.replace('_', ' ').title()}: {section_data}")
            
            return lines
        
        for section, data in specs.items():
            spec_lines.extend(format_spec_section(section, data))
        
        return "\n".join(spec_lines)
    
    def _split_long_content(self, content: str, config: ChunkConfig, 
                           base_metadata: Dict, section_name: str) -> List[Document]:
        """Split long content into multiple chunks with overlap"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap
        )
        
        chunks = []
        splits = splitter.split_text(content)
        
        for i, split in enumerate(splits):
            chunk_metadata = {
                **base_metadata,
                "chunk_type": "section",
                "section": section_name,
                "section_part": i + 1,
                "total_parts": len(splits),
                "boost_score": 1.0
            }
            
            chunks.append(Document(
                page_content=split,
                metadata=chunk_metadata
            ))
        
        return chunks
    
    def _create_review_summary(self, reviews: Dict[str, Any]) -> str:
        """Create a summary of product reviews"""
        summary_parts = [
            f"Customer Reviews Summary:",
            f"Average Rating: {reviews['average_rating']}/5 stars",
            f"Total Reviews: {reviews['total_reviews']}",
        ]
        
        # Rating distribution
        dist = reviews.get("rating_distribution", {})
        if dist:
            summary_parts.append("Rating Distribution:")
            for rating, count in sorted(dist.items(), reverse=True):
                percentage = (count / reviews['total_reviews']) * 100
                summary_parts.append(f"  {rating.replace('_', ' ')}: {count} ({percentage:.1f}%)")
        
        # Featured reviews
        if reviews.get("featured_reviews"):
            summary_parts.append("\nFeatured Customer Reviews:")
            for review in reviews["featured_reviews"][:2]:  # Top 2 reviews
                verified = " (Verified)" if review.get("verified_purchase") else ""
                summary_parts.append(f"• {review['title']} ({review['rating']}/5){verified}: {review['content'][:150]}...")
        
        return "\n".join(summary_parts)
    
    def _format_warranty_info(self, warranty: Dict[str, Any]) -> str:
        """Format warranty information"""
        warranty_parts = [
            f"Warranty Information:",
            f"Duration: {warranty.get('duration', 'N/A')}",
            f"Type: {warranty.get('type', 'Standard Warranty')}",
        ]
        
        if warranty.get("coverage"):
            warranty_parts.append(f"Coverage: {', '.join(warranty['coverage'])}")
        
        if warranty.get("support"):
            warranty_parts.append(f"Support: {warranty['support']}")
        
        return "\n".join(warranty_parts)

    def process_policy_documents(self) -> List[Document]:
        """Process policy documents with appropriate chunking"""
        chunks = []
        
        # Process detailed policies
        try:
            with open("ecommerce-practice-data/detailed_policies.md", "r", encoding="utf-8") as f:
                policy_content = f.read()
            
            # Split policies by sections (## headers)
            sections = policy_content.split("## ")
            
            for i, section in enumerate(sections):
                if not section.strip():
                    continue
                    
                # Extract section title
                lines = section.strip().split("\n")
                section_title = lines[0] if lines else f"Section {i}"
                section_content = "\n".join(lines[1:]) if len(lines) > 1 else section
                
                # Create chunks for this section
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=CHUNK_CONFIGS["policy"].chunk_size,
                    chunk_overlap=CHUNK_CONFIGS["policy"].chunk_overlap
                )
                
                splits = splitter.split_text(section_content)
                
                for j, split in enumerate(splits):
                    chunks.append(Document(
                        page_content=f"Policy Section: {section_title}\n\n{split}",
                        metadata={
                            "content_type": "policy",
                            "section": section_title.lower().replace(" ", "_"),
                            "chunk_type": "section",
                            "section_part": j + 1,
                            "total_parts": len(splits),
                            "source": "detailed_policies.md",
                            "boost_score": 1.0
                        }
                    ))
        except FileNotFoundError:
            print("Warning: detailed_policies.md not found")
        
        return chunks

    def process_faq_documents(self) -> List[Document]:
        """Process FAQ documents with Q&A aware chunking"""
        chunks = []
        
        try:
            with open("ecommerce-practice-data/comprehensive_faq.md", "r", encoding="utf-8") as f:
                faq_content = f.read()
            
            # Split by main sections (## headers)
            sections = faq_content.split("## ")
            
            for section in sections:
                if not section.strip():
                    continue
                
                lines = section.strip().split("\n")
                section_title = lines[0] if lines else "FAQ Section"
                section_content = "\n".join(lines[1:]) if len(lines) > 1 else section
                
                # Split by Q&A pairs (### headers)
                qa_pairs = section_content.split("### ")
                
                for qa in qa_pairs:
                    if not qa.strip():
                        continue
                    
                    qa_lines = qa.strip().split("\n")
                    question = qa_lines[0] if qa_lines else "Question"
                    answer = "\n".join(qa_lines[1:]) if len(qa_lines) > 1 else ""
                    
                    if len(answer) > CHUNK_CONFIGS["faq"].chunk_size:
                        # Split long answers
                        splitter = RecursiveCharacterTextSplitter(
                            chunk_size=CHUNK_CONFIGS["faq"].chunk_size,
                            chunk_overlap=CHUNK_CONFIGS["faq"].chunk_overlap
                        )
                        splits = splitter.split_text(answer)
                        
                        for i, split in enumerate(splits):
                            chunks.append(Document(
                                page_content=f"Q: {question}\nA: {split}",
                                metadata={
                                    "content_type": "faq",
                                    "section": section_title.lower().replace(" ", "_"),
                                    "question": question,
                                    "chunk_type": "qa_pair",
                                    "part": i + 1,
                                    "total_parts": len(splits),
                                    "source": "comprehensive_faq.md",
                                    "boost_score": 1.1  # Boost FAQ for support queries
                                }
                            ))
                    else:
                        # Single chunk for short Q&A
                        chunks.append(Document(
                            page_content=f"Q: {question}\nA: {answer}",
                            metadata={
                                "content_type": "faq",
                                "section": section_title.lower().replace(" ", "_"),
                                "question": question,
                                "chunk_type": "qa_pair",
                                "source": "comprehensive_faq.md",
                                "boost_score": 1.1
                            }
                        ))
        except FileNotFoundError:
            print("Warning: comprehensive_faq.md not found")
        
        return chunks

def main():
    print("Starting Enhanced Hybrid Chunking Process...")
    
    chunker = HybridChunker()
    all_chunks = []
    
    # Process large complex product catalog
    print("Processing complex product catalog...")
    try:
        with open("ecommerce-practice-data/large_complex_catalog.json", "r", encoding="utf-8") as f:
            products = json.load(f)
        
        product_chunks = 0
        for i, product in enumerate(products):
            chunks = chunker.create_product_chunks(product)
            all_chunks.extend(chunks)
            product_chunks += len(chunks)
            
            if (i + 1) % 50 == 0:
                print(f"Processed {i + 1} products, created {product_chunks} chunks so far...")
        
        print(f"Created {product_chunks} chunks from {len(products)} products")
        
    except FileNotFoundError:
        print("Warning: large_complex_catalog.json not found, skipping products")
    
    # Process policy documents
    print("Processing policy documents...")
    policy_chunks = chunker.process_policy_documents()
    all_chunks.extend(policy_chunks)
    print(f"Created {len(policy_chunks)} policy chunks")
    
    # Process FAQ documents
    print("Processing FAQ documents...")
    faq_chunks = chunker.process_faq_documents()
    all_chunks.extend(faq_chunks)
    print(f"Created {len(faq_chunks)} FAQ chunks")
    
    print(f"\nTotal chunks created: {len(all_chunks)}")
    
    # Analyze chunk distribution
    chunk_types = {}
    content_types = {}
    for chunk in all_chunks:
        chunk_type = chunk.metadata.get("chunk_type", "unknown")
        content_type = chunk.metadata.get("content_type", "unknown")
        
        chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
        content_types[content_type] = content_types.get(content_type, 0) + 1
    
    print("\n=== CHUNK ANALYSIS ===")
    print("By Chunk Type:")
    for chunk_type, count in sorted(chunk_types.items()):
        print(f"  {chunk_type}: {count}")
    
    print("\nBy Content Type:")
    for content_type, count in sorted(content_types.items()):
        print(f"  {content_type}: {count}")
    
    # Create enhanced vector database
    print("\nCreating enhanced vector database...")
    try:
        vectorstore = Chroma.from_documents(
            documents=all_chunks,
            embedding=chunker.embeddings,
            persist_directory="ecommerce-practice-data/enhanced_vector_db"
        )
        vectorstore.persist()
        print(f"Enhanced vector database created successfully!")
        print(f"Database location: enhanced_vector_db/")
        
    except Exception as e:
        print(f"Error creating vector database: {e}")
        return
    
    print("\n=== IMPLEMENTATION COMPLETE ===")
    print("Next steps:")
    print("1. Test retrieval with enhanced_assistant.py")
    print("2. Run sample queries to verify chunking quality")
    print("3. Monitor performance and tune boost scores if needed")

if __name__ == "__main__":
    main()