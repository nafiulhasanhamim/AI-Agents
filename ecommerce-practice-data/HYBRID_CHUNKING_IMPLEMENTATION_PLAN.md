# Hybrid Chunking Implementation Plan for VibeShop

## Overview
This plan implements the ChatGPT-recommended hybrid chunking strategy with canonical summaries, section-based chunks, and rich metadata for enhanced e-commerce RAG performance.

## Phase 1: Enhanced Data Structure & Metadata

### 1.1 Product Data Enhancement ✅ COMPLETED
- Created `enhanced_product_catalog.json` with complex product specifications
- Added detailed descriptions, reviews, warranties, and technical specs
- Implemented rich metadata structure for filtering and categorization

### 1.2 Content Type Diversification ✅ COMPLETED
- Created `detailed_policies.md` with comprehensive policy information
- Added `comprehensive_faq.md` with detailed Q&A content
- Developed `product_reviews_database.md` with authentic review data

### 1.3 Metadata Schema Design
```python
# Standard metadata fields for all chunks
base_metadata = {
    "content_type": str,      # "product", "policy", "faq", "review"
    "source": str,            # filename or source identifier
    "last_updated": str,      # ISO date format
    "chunk_type": str,        # "summary", "section", "full"
    "section": str,           # specific section name (optional)
}

# Product-specific metadata
product_metadata = {
    "product_id": str,
    "product_name": str,
    "category": str,
    "subcategory": str,
    "brand": str,
    "price": float,
    "currency": str,
    "in_stock": bool,
    "on_sale": bool,
    "rating": float,
    "review_count": int
}
```

## Phase 2: Hybrid Chunking Implementation

### 2.1 Create Enhanced Index Documents Script
```python
# File: enhanced_index_documents.py

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

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
        chunks = []
        base_metadata = {
            "content_type": "product",
            "product_id": product["id"],
            "product_name": product["name"],
            "category": product["category"],
            "brand": product["brand"],
            "price": product["price"],
            "currency": product["currency"],
            "in_stock": product["in_stock"],
            "on_sale": product.get("on_sale", False),
            "last_updated": product["last_updated"]
        }
        
        # 1. Canonical Summary Chunk (ALWAYS CREATED)
        summary_text = self._create_canonical_summary(product)
        chunks.append(Document(
            page_content=summary_text,
            metadata={
                **base_metadata,
                "chunk_type": "summary",
                "boost_score": 1.2  # Boost for retrieval
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
                    "section": "specifications"
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
                    "section": "features"
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
        if product.get("reviews"):
            review_summary = self._create_review_summary(product["reviews"])
            chunks.append(Document(
                page_content=review_summary,
                metadata={
                    **base_metadata,
                    "chunk_type": "section",
                    "section": "reviews",
                    "rating": product["reviews"]["average_rating"],
                    "review_count": product["reviews"]["total_reviews"]
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
        
        if product.get("in_stock"):
            summary_parts.append("Status: In Stock")
        else:
            summary_parts.append("Status: Out of Stock")
            
        if product.get("on_sale"):
            summary_parts.append(f"On Sale: {product.get('discount_percent', 0)}% off")
        
        if product.get("reviews", {}).get("average_rating"):
            rating = product["reviews"]["average_rating"]
            count = product["reviews"]["total_reviews"]
            summary_parts.append(f"Rating: {rating}/5 ({count} reviews)")
        
        return ". ".join(summary_parts) + "."
    
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
                "total_parts": len(splits)
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
            summary_parts.append("\nFeatured Reviews:")
            for review in reviews["featured_reviews"][:2]:  # Top 2 reviews
                summary_parts.append(f"• {review['title']} ({review['rating']}/5): {review['content'][:200]}...")
        
        return "\n".join(summary_parts)

def main():
    chunker = HybridChunker()
    all_chunks = []
    
    # Process enhanced product catalog
    with open("enhanced_product_catalog.json", "r") as f:
        products = json.load(f)
    
    for product in products:
        product_chunks = chunker.create_product_chunks(product)
        all_chunks.extend(product_chunks)
        print(f"Created {len(product_chunks)} chunks for {product['name']}")
    
    # Process policy documents
    policy_chunks = process_policy_documents()
    all_chunks.extend(policy_chunks)
    
    # Process FAQ documents
    faq_chunks = process_faq_documents()
    all_chunks.extend(faq_chunks)
    
    # Process review documents
    review_chunks = process_review_documents()
    all_chunks.extend(review_chunks)
    
    print(f"Total chunks created: {len(all_chunks)}")
    
    # Create vector database
    print("Creating vector database...")
    vectorstore = Chroma.from_documents(
        documents=all_chunks,
        embedding=chunker.embeddings,
        persist_directory="enhanced_vector_db"
    )
    vectorstore.persist()
    print("Vector database created successfully!")

if __name__ == "__main__":
    main()
```

### 2.2 Enhanced Retrieval System
```python
# File: enhanced_assistant.py

from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

class EnhancedRetriever:
    def __init__(self, vectorstore: Chroma):
        self.vectorstore = vectorstore
        
    def retrieve_with_metadata_filtering(self, 
                                       query: str, 
                                       filters: Optional[Dict[str, Any]] = None,
                                       k: int = 10) -> List[Document]:
        """Retrieve documents with metadata filtering and boosting"""
        
        # Extract structured filters from query
        extracted_filters = self._extract_filters_from_query(query)
        if filters:
            extracted_filters.update(filters)
        
        # Perform vector search with metadata filters
        if extracted_filters:
            docs = self.vectorstore.similarity_search(
                query, 
                k=k,
                filter=extracted_filters
            )
        else:
            docs = self.vectorstore.similarity_search(query, k=k)
        
        # Apply boosting and reranking
        scored_docs = self._apply_boosting_and_reranking(docs, query, extracted_filters)
        
        return scored_docs
    
    def _extract_filters_from_query(self, query: str) -> Dict[str, Any]:
        """Extract structured filters from natural language query"""
        filters = {}
        query_lower = query.lower()
        
        # Price range extraction
        import re
        price_patterns = [
            r'under \$?(\d+)',
            r'less than \$?(\d+)',
            r'below \$?(\d+)',
            r'cheaper than \$?(\d+)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, query_lower)
            if match:
                filters["price"] = {"$lt": float(match.group(1))}
                break
        
        # Category extraction
        categories = ["laptop", "phone", "smartphone", "computer", "gaming", "electronics"]
        for category in categories:
            if category in query_lower:
                filters["category"] = {"$regex": f".*{category}.*", "$options": "i"}
                break
        
        # Brand extraction
        brands = ["titan", "apex", "apple", "samsung", "dell", "hp"]
        for brand in brands:
            if brand in query_lower:
                filters["brand"] = {"$regex": f".*{brand}.*", "$options": "i"}
                break
        
        # Stock status
        if any(phrase in query_lower for phrase in ["in stock", "available"]):
            filters["in_stock"] = True
        
        # Sale status
        if any(phrase in query_lower for phrase in ["on sale", "discount", "deal"]):
            filters["on_sale"] = True
        
        return filters
    
    def _apply_boosting_and_reranking(self, 
                                    docs: List[Document], 
                                    query: str, 
                                    filters: Dict[str, Any]) -> List[Document]:
        """Apply boosting to summary chunks and rerank results"""
        
        scored_docs = []
        for doc in docs:
            score = 1.0
            
            # Boost summary chunks
            if doc.metadata.get("chunk_type") == "summary":
                score *= doc.metadata.get("boost_score", 1.2)
            
            # Boost exact metadata matches
            metadata_match_score = self._calculate_metadata_match_score(doc.metadata, filters)
            score *= (1 + 0.3 * metadata_match_score)
            
            # Boost highly rated products
            if doc.metadata.get("rating"):
                rating_boost = doc.metadata["rating"] / 5.0 * 0.1
                score *= (1 + rating_boost)
            
            scored_docs.append((doc, score))
        
        # Sort by score and return documents
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, score in scored_docs]
    
    def _calculate_metadata_match_score(self, 
                                      metadata: Dict[str, Any], 
                                      filters: Dict[str, Any]) -> float:
        """Calculate how well metadata matches the filters"""
        if not filters:
            return 0.0
        
        matches = 0
        total_filters = len(filters)
        
        for key, filter_value in filters.items():
            if key in metadata:
                if isinstance(filter_value, dict):
                    # Handle complex filters like price ranges
                    if "$lt" in filter_value and metadata[key] < filter_value["$lt"]:
                        matches += 1
                    elif "$gt" in filter_value and metadata[key] > filter_value["$gt"]:
                        matches += 1
                    elif "$regex" in filter_value:
                        import re
                        if re.search(filter_value["$regex"], str(metadata[key]), 
                                   re.IGNORECASE if filter_value.get("$options") == "i" else 0):
                            matches += 1
                else:
                    # Direct value match
                    if metadata[key] == filter_value:
                        matches += 1
        
        return matches / total_filters if total_filters > 0 else 0.0

class EnhancedAssistant:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = Chroma(
            persist_directory="enhanced_vector_db",
            embedding_function=self.embeddings
        )
        self.retriever = EnhancedRetriever(self.vectorstore)
        self.llm = ChatGoogleGenerativeAI(model="gemini-exp-1206", temperature=0)
        
    def query(self, user_query: str, chat_history: str = "") -> str:
        """Process user query with enhanced retrieval and response generation"""
        
        # Step 1: Retrieve relevant documents
        relevant_docs = self.retriever.retrieve_with_metadata_filtering(user_query)
        
        # Step 2: Separate summary and detail chunks
        summary_chunks = [doc for doc in relevant_docs if doc.metadata.get("chunk_type") == "summary"]
        detail_chunks = [doc for doc in relevant_docs if doc.metadata.get("chunk_type") == "section"]
        
        # Step 3: Format context for LLM
        context = self._format_context(summary_chunks, detail_chunks)
        
        # Step 4: Generate response
        response = self._generate_response(user_query, context, chat_history)
        
        return response
    
    def _format_context(self, summary_chunks: List[Document], detail_chunks: List[Document]) -> str:
        """Format retrieved chunks into context for LLM"""
        context_parts = []
        
        if summary_chunks:
            context_parts.append("=== PRODUCT SUMMARIES ===")
            for doc in summary_chunks[:3]:  # Top 3 summaries
                context_parts.append(f"• {doc.page_content}")
                context_parts.append("")
        
        if detail_chunks:
            context_parts.append("=== DETAILED INFORMATION ===")
            for doc in detail_chunks[:5]:  # Top 5 detail chunks
                section = doc.metadata.get("section", "Details")
                context_parts.append(f"[{section.title()}]")
                context_parts.append(doc.page_content)
                context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _generate_response(self, query: str, context: str, chat_history: str) -> str:
        """Generate response using LLM with formatted context"""
        
        system_prompt = """You are VibeShop's AI Assistant, an expert in electronics and e-commerce.
        
        Use the provided context to answer customer questions accurately and helpfully.
        
        Guidelines:
        - Prioritize information from PRODUCT SUMMARIES for quick answers
        - Use DETAILED INFORMATION for comprehensive responses when needed
        - Always mention specific product names, prices, and key features
        - If comparing products, highlight key differences
        - For technical questions, provide specific specifications
        - Be conversational and helpful, not robotic
        - If you don't have enough information, say so clearly
        
        Context:
        {context}
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Chat History:\n{chat_history}\n\nCurrent Question: {query}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "context": context,
            "chat_history": chat_history,
            "query": query
        })
        
        return response.content

def main():
    assistant = EnhancedAssistant()
    
    print("Enhanced VibeShop Assistant Ready!")
    print("Try queries like:")
    print("- 'Show me gaming laptops under $2000'")
    print("- 'What's the best camera phone?'")
    print("- 'Compare the Titan laptop specs'")
    print("- 'What's your return policy?'")
    print()
    
    while True:
        query = input("You: ")
        if query.lower() in ["exit", "quit"]:
            break
            
        try:
            response = assistant.query(query)
            print(f"Assistant: {response}\n")
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()
```

## Phase 3: Implementation Steps

### 3.1 File Structure
```
ecommerce-practice-data/
├── enhanced_product_catalog.json          ✅ Created
├── detailed_policies.md                   ✅ Created  
├── comprehensive_faq.md                    ✅ Created
├── product_reviews_database.md             ✅ Created
├── enhanced_index_documents.py             📝 To Create
├── enhanced_assistant.py                   📝 To Create
├── hybrid_chunking_utils.py                📝 To Create
├── enhanced_vector_db/                     📝 To Create
├── config/
│   ├── chunk_configs.json                  📝 To Create
│   └── metadata_schema.json                📝 To Create
└── tests/
    ├── test_chunking.py                     📝 To Create
    ├── test_retrieval.py                   📝 To Create
    └── test_integration.py                 📝 To Create
```

### 3.2 Implementation Timeline

#### Week 1: Core Implementation
- [ ] Create `enhanced_index_documents.py` with hybrid chunking logic
- [ ] Implement `HybridChunker` class with product-specific chunking
- [ ] Create enhanced metadata extraction and validation
- [ ] Test chunking with sample products

#### Week 2: Retrieval Enhancement  
- [ ] Implement `EnhancedRetriever` with metadata filtering
- [ ] Add boosting and reranking algorithms
- [ ] Create query analysis and filter extraction
- [ ] Test retrieval accuracy and performance

#### Week 3: Integration & Testing
- [ ] Integrate enhanced assistant with Streamlit app
- [ ] Create comprehensive test suite
- [ ] Performance optimization and tuning
- [ ] Documentation and examples

#### Week 4: Advanced Features
- [ ] Add semantic search improvements
- [ ] Implement conversation memory
- [ ] Create admin dashboard for chunk management
- [ ] Deploy and monitor performance

### 3.3 Success Metrics

#### Retrieval Quality
- **Precision@5**: >85% for product queries
- **Category Accuracy**: >90% for filtered searches  
- **Price Filter Accuracy**: >95% for price-based queries
- **Response Relevance**: >4.0/5.0 user rating

#### Performance Metrics
- **Query Response Time**: <2 seconds average
- **Index Build Time**: <5 minutes for full catalog
- **Memory Usage**: <2GB for vector database
- **Concurrent Users**: Support 100+ simultaneous queries

#### Business Metrics
- **User Satisfaction**: >4.2/5.0 rating
- **Query Success Rate**: >90% successful responses
- **Conversion Rate**: Track product page visits from recommendations
- **Support Ticket Reduction**: 30% reduction in basic product questions

## Phase 4: Advanced Features (Future)

### 4.1 Semantic Search Enhancements
- Implement cross-encoder reranking for better relevance
- Add query expansion using synonyms and related terms
- Create product similarity clustering for better recommendations

### 4.2 Conversational Memory
- Implement conversation context tracking
- Add user preference learning
- Create personalized product recommendations

### 4.3 Multi-Modal Support
- Add image search capabilities for products
- Implement visual similarity matching
- Create image-to-text product descriptions

### 4.4 Real-Time Updates
- Implement incremental index updates
- Add real-time inventory synchronization
- Create dynamic pricing updates in chunks

## Conclusion

This implementation plan provides a comprehensive approach to upgrading the ecommerce-practice-data project with advanced hybrid chunking strategies. The phased approach ensures manageable development while delivering immediate improvements in search accuracy and user experience.

The enhanced system will support complex product catalogs, precise filtering, and intelligent retrieval while maintaining the simplicity needed for development and maintenance.