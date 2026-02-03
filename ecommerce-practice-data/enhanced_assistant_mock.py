import os
import re
from typing import List, Dict, Any, Optional
import random

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

class MockEnhancedRetriever:
    def __init__(self, vectorstore: Chroma):
        self.vectorstore = vectorstore
        
    def retrieve_with_metadata_filtering(self, 
                                       query: str, 
                                       filters: Optional[Dict[str, Any]] = None,
                                       k: int = 15) -> List[Document]:
        """Retrieve documents with metadata filtering and boosting"""
        
        # Extract structured filters from query
        extracted_filters = self._extract_filters_from_query(query)
        if filters:
            extracted_filters.update(filters)
        
        print(f"🔍 Query: {query}")
        print(f"📊 Extracted filters: {extracted_filters}")
        
        # Perform vector search with metadata filters
        try:
            if extracted_filters:
                docs = self.vectorstore.similarity_search(
                    query, 
                    k=k,
                    filter=extracted_filters
                )
            else:
                docs = self.vectorstore.similarity_search(query, k=k)
        except Exception as e:
            print(f"⚠️ Filter search failed: {e}, falling back to basic search")
            docs = self.vectorstore.similarity_search(query, k=k)
        
        print(f"📄 Retrieved {len(docs)} documents before boosting")
        
        # Apply boosting and reranking
        scored_docs = self._apply_boosting_and_reranking(docs, query, extracted_filters)
        
        return scored_docs[:k]  # Return top k after reranking
    
    def _extract_filters_from_query(self, query: str) -> Dict[str, Any]:
        """Extract structured filters from natural language query"""
        filters = {}
        query_lower = query.lower()
        
        # Price range extraction
        price_patterns = [
            (r'under \$?(\d+)', 'lt'),
            (r'less than \$?(\d+)', 'lt'),
            (r'below \$?(\d+)', 'lt'),
            (r'cheaper than \$?(\d+)', 'lt'),
            (r'over \$?(\d+)', 'gt'),
            (r'more than \$?(\d+)', 'gt'),
            (r'above \$?(\d+)', 'gt'),
            (r'between \$?(\d+) and \$?(\d+)', 'range')
        ]
        
        for pattern, op_type in price_patterns:
            match = re.search(pattern, query_lower)
            if match:
                if op_type == 'range':
                    min_price, max_price = float(match.group(1)), float(match.group(2))
                    filters["price"] = {"$gte": min_price, "$lte": max_price}
                elif op_type == 'lt':
                    filters["price"] = {"$lt": float(match.group(1))}
                elif op_type == 'gt':
                    filters["price"] = {"$gt": float(match.group(1))}
                break
        
        # Category extraction
        category_keywords = {
            "laptop": "Gaming Laptops",
            "gaming laptop": "Gaming Laptops", 
            "computer": "Gaming Laptops",
            "phone": "Smartphones",
            "smartphone": "Smartphones",
            "mobile": "Smartphones",
            "headphone": "Headphones",
            "audio": "Headphones",
            "earphone": "Headphones",
            "console": "Consoles",
            "gaming console": "Consoles",
            "appliance": "Appliances",
            "kitchen": "Appliances"
        }
        
        for keyword, category in category_keywords.items():
            if keyword in query_lower:
                filters["category"] = {"$regex": f".*{category}.*"}
                break
        
        # Brand extraction
        brands = ["titan", "apex", "vortex", "phoenix", "storm", "quantum", "nova", "stellar", "pulse",
                 "soundwave", "audiotech", "harmony", "resonance", "echo", "gameforce", "playmax", 
                 "ultrabox", "neostation", "chefmaster", "cookpro", "kitchenelite", "hometech"]
        
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
        
        # Content type filters
        if any(phrase in query_lower for phrase in ["policy", "return", "shipping", "warranty"]):
            filters["content_type"] = "policy"
        elif any(phrase in query_lower for phrase in ["faq", "question", "how to", "help"]):
            filters["content_type"] = "faq"
        
        return filters
    
    def _apply_boosting_and_reranking(self, 
                                    docs: List[Document], 
                                    query: str, 
                                    filters: Dict[str, Any]) -> List[Document]:
        """Apply boosting to summary chunks and rerank results"""
        
        scored_docs = []
        for doc in docs:
            score = 1.0
            
            # Boost summary chunks (highest priority)
            if doc.metadata.get("chunk_type") == "summary":
                score *= doc.metadata.get("boost_score", 1.3)
            
            # Boost based on content type relevance
            boost_score = doc.metadata.get("boost_score", 1.0)
            score *= boost_score
            
            # Boost exact metadata matches
            metadata_match_score = self._calculate_metadata_match_score(doc.metadata, filters)
            score *= (1 + 0.4 * metadata_match_score)  # Increased metadata boost
            
            # Boost highly rated products
            if doc.metadata.get("rating") and doc.metadata["rating"] > 0:
                rating_boost = (doc.metadata["rating"] / 5.0) * 0.15
                score *= (1 + rating_boost)
            
            # Boost in-stock items slightly
            if doc.metadata.get("in_stock"):
                score *= 1.05
            
            # Boost sale items for deal-related queries
            if "deal" in query.lower() or "sale" in query.lower():
                if doc.metadata.get("on_sale"):
                    score *= 1.2
            
            scored_docs.append((doc, score))
        
        # Sort by score and return documents
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        print(f"🎯 Top 5 scores after boosting: {[f'{score:.2f}' for _, score in scored_docs[:5]]}")
        
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
                    elif "$gte" in filter_value and "$lte" in filter_value:
                        if filter_value["$gte"] <= metadata[key] <= filter_value["$lte"]:
                            matches += 1
                    elif "$regex" in filter_value:
                        import re
                        flags = re.IGNORECASE if filter_value.get("$options") == "i" else 0
                        if re.search(filter_value["$regex"], str(metadata[key]), flags):
                            matches += 1
                else:
                    # Direct value match
                    if metadata[key] == filter_value:
                        matches += 1
        
        return matches / total_filters if total_filters > 0 else 0.0

class MockEnhancedAssistant:
    def __init__(self):
        print("🤖 Initializing Mock Enhanced Assistant...")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Load vector database with robust path handling
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, "enhanced_vector_db")
        
        # Alternative paths to try
        alternative_paths = [
            db_path,
            "ecommerce-practice-data/enhanced_vector_db",
            os.path.join(os.getcwd(), "ecommerce-practice-data", "enhanced_vector_db"),
            "enhanced_vector_db"
        ]
        
        db_path_found = None
        for path in alternative_paths:
            if os.path.exists(path):
                db_path_found = path
                print(f"📁 Found vector database at: {path}")
                break
        
        if not db_path_found:
            raise FileNotFoundError(f"Vector database not found. Tried paths: {alternative_paths}. Please run enhanced_index_documents.py first.")
        
        self.vectorstore = Chroma(
            persist_directory=db_path_found,
            embedding_function=self.embeddings
        )
        
        self.retriever = MockEnhancedRetriever(self.vectorstore)
        
        # Mock response templates
        self.response_templates = {
            "gaming_laptop": [
                "I found several excellent gaming laptops that match your criteria:",
                "Here are some great gaming laptop options for you:",
                "Based on your requirements, I recommend these gaming laptops:"
            ],
            "smartphone": [
                "I found some fantastic smartphones that would be perfect for you:",
                "Here are the top smartphone recommendations based on your query:",
                "These smartphones match what you're looking for:"
            ],
            "headphones": [
                "I found some excellent headphones that match your preferences:",
                "Here are my top headphone recommendations:",
                "These headphones would be perfect for your needs:"
            ],
            "policy": [
                "Here's the information about our policies:",
                "I can help you with that policy question:",
                "Let me explain our policy on this matter:"
            ],
            "general": [
                "Based on your query, here's what I found:",
                "I can help you with that! Here's the information:",
                "Great question! Here's what I can tell you:"
            ]
        }
        
        print("✅ Mock Enhanced Assistant initialized successfully!")
        
    def query(self, user_query: str, chat_history: str = "") -> str:
        """Process user query with enhanced retrieval and mock response generation"""
        
        print(f"\n🔍 Processing Query: {user_query}")
        
        # Step 1: Retrieve relevant documents
        relevant_docs = self.retriever.retrieve_with_metadata_filtering(user_query)
        
        # Step 2: Separate different chunk types
        summary_chunks = [doc for doc in relevant_docs if doc.metadata.get("chunk_type") == "summary"]
        detail_chunks = [doc for doc in relevant_docs if doc.metadata.get("chunk_type") in ["section", "qa_pair"]]
        
        print(f"📊 Retrieved: {len(summary_chunks)} summaries, {len(detail_chunks)} detail chunks")
        
        # Step 3: Generate mock response based on retrieved content
        response = self._generate_mock_response(user_query, summary_chunks, detail_chunks)
        
        return response
    
    def _generate_mock_response(self, query: str, summary_chunks: List[Document], detail_chunks: List[Document]) -> str:
        """Generate a realistic mock response based on retrieved chunks"""
        
        query_lower = query.lower()
        
        # Determine response type
        if any(word in query_lower for word in ["laptop", "gaming", "computer"]):
            template_key = "gaming_laptop"
        elif any(word in query_lower for word in ["phone", "smartphone", "mobile"]):
            template_key = "smartphone"
        elif any(word in query_lower for word in ["headphone", "audio", "earphone"]):
            template_key = "headphones"
        elif any(word in query_lower for word in ["policy", "return", "shipping", "warranty"]):
            template_key = "policy"
        else:
            template_key = "general"
        
        # Start with template
        response_parts = [random.choice(self.response_templates[template_key])]
        response_parts.append("")
        
        # Add product information from summary chunks
        if summary_chunks and template_key != "policy":
            for i, doc in enumerate(summary_chunks[:3], 1):
                # Extract product info from metadata
                product_name = doc.metadata.get("product_name", "Unknown Product")
                price = doc.metadata.get("price", 0)
                rating = doc.metadata.get("rating", 0)
                review_count = doc.metadata.get("review_count", 0)
                brand = doc.metadata.get("brand", "Unknown")
                in_stock = doc.metadata.get("in_stock", True)
                on_sale = doc.metadata.get("on_sale", False)
                
                # Format product entry
                product_info = f"{i}. **{product_name}** - ${price:,.2f}"
                
                if on_sale:
                    product_info += " 🔥 **ON SALE**"
                
                response_parts.append(product_info)
                response_parts.append(f"   - Brand: {brand}")
                
                if rating > 0:
                    stars = "⭐" * int(rating)
                    response_parts.append(f"   - Rating: {stars} {rating}/5 ({review_count} reviews)")
                
                stock_status = "✅ In Stock" if in_stock else "❌ Out of Stock"
                response_parts.append(f"   - Status: {stock_status}")
                
                # Add some content from the chunk
                content_preview = doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
                response_parts.append(f"   - {content_preview}")
                response_parts.append("")
        
        # Add policy information
        elif detail_chunks and template_key == "policy":
            for doc in detail_chunks[:2]:
                section = doc.metadata.get("section", "Policy")
                content_preview = doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
                response_parts.append(f"**{section.replace('_', ' ').title()}:**")
                response_parts.append(content_preview)
                response_parts.append("")
        
        # Add helpful suggestions
        if template_key == "gaming_laptop":
            response_parts.append("💡 **Need help deciding?** I can provide detailed specifications, compare models, or help you find laptops in a specific price range!")
        elif template_key == "smartphone":
            response_parts.append("📱 **Want more details?** I can compare camera specs, battery life, or help you find phones with specific features!")
        elif template_key == "headphones":
            response_parts.append("🎧 **Looking for specifics?** I can help you compare sound quality, battery life, or find headphones for specific use cases!")
        elif template_key == "policy":
            response_parts.append("❓ **Have more questions?** Feel free to ask about specific policy details or other store policies!")
        
        # Add search stats
        response_parts.append("")
        response_parts.append(f"🔍 *Searched {len(summary_chunks + detail_chunks)} relevant items from our enhanced database*")
        
        return "\n".join(response_parts)

def get_mock_enhanced_assistant():
    """Factory function to create mock enhanced assistant"""
    try:
        return MockEnhancedAssistant()
    except Exception as e:
        print(f"❌ Failed to create mock assistant: {e}")
        return None

def main():
    """Test the mock enhanced assistant"""
    try:
        assistant = MockEnhancedAssistant()
    except Exception as e:
        print(f"Failed to initialize mock assistant: {e}")
        return
    
    print("\n🛍️ Mock Enhanced VibeShop Assistant Ready!")
    print("✨ This version works without API calls - perfect for testing!")
    print("\nTry these sample queries:")
    print("- 'Show me gaming laptops under $2000'")
    print("- 'What's the best Titan laptop?'")
    print("- 'Compare smartphone cameras'")
    print("- 'What's your return policy?'")
    print("- 'Show me products on sale'")
    print("\nType 'exit' to quit\n")
    
    chat_history = []
    
    while True:
        try:
            query = input("You: ").strip()
            if not query:
                continue
                
            if query.lower() in ["exit", "quit", "bye"]:
                print("Assistant: Thank you for testing VibeShop! The hybrid chunking system is working great! 🛍️")
                break
                
            # Convert chat history to string
            history_str = "\n".join(chat_history[-6:])  # Keep last 6 exchanges
            
            response = assistant.query(query, history_str)
            print(f"\nAssistant: {response}\n")
            
            # Update chat history
            chat_history.append(f"Human: {query}")
            chat_history.append(f"Assistant: {response}")
            
        except KeyboardInterrupt:
            print("\n\nAssistant: Goodbye! 👋")
            break
        except Exception as e:
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    main()