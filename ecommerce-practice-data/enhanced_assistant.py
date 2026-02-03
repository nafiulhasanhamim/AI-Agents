import os
import re
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

class EnhancedRetriever:
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
        
        print(f"Query: {query}")
        print(f"Extracted filters: {extracted_filters}")
        
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
            print(f"Filter search failed: {e}, falling back to basic search")
            docs = self.vectorstore.similarity_search(query, k=k)
        
        print(f"Retrieved {len(docs)} documents before boosting")
        
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
        
        print(f"Top 5 scores after boosting: {[f'{score:.2f}' for _, score in scored_docs[:5]]}")
        
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

class EnhancedAssistant:
    def __init__(self):
        print("Initializing Enhanced Assistant...")
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
                print(f"Found vector database at: {path}")
                break
        
        if not db_path_found:
            raise FileNotFoundError(f"Vector database not found. Tried paths: {alternative_paths}. Please run enhanced_index_documents.py first.")
        
        self.vectorstore = Chroma(
            persist_directory=db_path_found,
            embedding_function=self.embeddings
        )
        
        self.retriever = EnhancedRetriever(self.vectorstore)
        
        # Initialize LLM
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.llm = ChatGoogleGenerativeAI(model="gemini-exp-1206", temperature=0)
        print("Enhanced Assistant initialized successfully!")
        
    def query(self, user_query: str, chat_history: str = "") -> str:
        """Process user query with enhanced retrieval and response generation"""
        
        print(f"\n=== Processing Query: {user_query} ===")
        
        # Step 1: Retrieve relevant documents
        relevant_docs = self.retriever.retrieve_with_metadata_filtering(user_query)
        
        # Step 2: Separate different chunk types
        summary_chunks = [doc for doc in relevant_docs if doc.metadata.get("chunk_type") == "summary"]
        detail_chunks = [doc for doc in relevant_docs if doc.metadata.get("chunk_type") in ["section", "qa_pair"]]
        
        print(f"Retrieved: {len(summary_chunks)} summaries, {len(detail_chunks)} detail chunks")
        
        # Step 3: Format context for LLM
        context = self._format_context(summary_chunks, detail_chunks, user_query)
        
        # Step 4: Generate response
        response = self._generate_response(user_query, context, chat_history)
        
        return response
    
    def _format_context(self, summary_chunks: List[Document], detail_chunks: List[Document], query: str) -> str:
        """Format retrieved chunks into context for LLM"""
        context_parts = []
        
        # Always include summaries first (most important)
        if summary_chunks:
            context_parts.append("=== PRODUCT SUMMARIES ===")
            for i, doc in enumerate(summary_chunks[:5]):  # Top 5 summaries
                context_parts.append(f"{i+1}. {doc.page_content}")
                context_parts.append("")
        
        # Include relevant detail chunks
        if detail_chunks:
            context_parts.append("=== DETAILED INFORMATION ===")
            
            # Group by content type for better organization
            policy_chunks = [doc for doc in detail_chunks if doc.metadata.get("content_type") == "policy"]
            faq_chunks = [doc for doc in detail_chunks if doc.metadata.get("content_type") == "faq"]
            product_chunks = [doc for doc in detail_chunks if doc.metadata.get("content_type") == "product"]
            
            # Add policy information if relevant
            if policy_chunks and any(word in query.lower() for word in ["policy", "return", "shipping", "warranty"]):
                context_parts.append("--- POLICIES ---")
                for doc in policy_chunks[:3]:
                    context_parts.append(doc.page_content)
                    context_parts.append("")
            
            # Add FAQ information if relevant
            if faq_chunks and any(word in query.lower() for word in ["how", "what", "why", "help", "question"]):
                context_parts.append("--- FREQUENTLY ASKED QUESTIONS ---")
                for doc in faq_chunks[:3]:
                    context_parts.append(doc.page_content)
                    context_parts.append("")
            
            # Add product details
            if product_chunks:
                context_parts.append("--- PRODUCT DETAILS ---")
                for doc in product_chunks[:4]:
                    section = doc.metadata.get("section", "Details")
                    product_name = doc.metadata.get("product_name", "Product")
                    context_parts.append(f"[{product_name} - {section.title()}]")
                    context_parts.append(doc.page_content)
                    context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _generate_response(self, query: str, context: str, chat_history: str) -> str:
        """Generate response using LLM with formatted context"""
        
        system_prompt = """You are VibeShop's AI Assistant, an expert in electronics and e-commerce.

Use the provided context to answer customer questions accurately and helpfully.

GUIDELINES:
- Prioritize information from PRODUCT SUMMARIES for quick answers
- Use DETAILED INFORMATION for comprehensive responses when needed
- Always mention specific product names, prices, and key features when recommending products
- For product comparisons, highlight key differences in specs and pricing
- For technical questions, provide specific specifications from the context
- For policy/FAQ questions, give clear, direct answers based on the provided information
- Be conversational and helpful, not robotic
- If comparing multiple products, present them in a clear, organized way
- Include pricing information when discussing products
- If you don't have enough information in the context, say so clearly

RESPONSE FORMAT:
- Start with a direct answer to the question
- Provide specific product recommendations with key details
- Include relevant specifications or policy information
- End with helpful next steps or additional suggestions if appropriate

Context:
{context}
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Chat History:\n{chat_history}\n\nCurrent Question: {query}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            response = chain.invoke({
                "context": context,
                "chat_history": chat_history,
                "query": query
            })
            return response
        except Exception as e:
            return f"I apologize, but I encountered an error processing your request: {str(e)}"

def main():
    try:
        assistant = EnhancedAssistant()
    except Exception as e:
        print(f"Failed to initialize assistant: {e}")
        return
    
    print("\n🛍️ Enhanced VibeShop Assistant Ready!")
    print("\nTry these sample queries:")
    print("- 'Show me gaming laptops under $2000'")
    print("- 'What's the best camera phone?'")
    print("- 'Compare Titan laptop specifications'")
    print("- 'What's your return policy for electronics?'")
    print("- 'Show me headphones on sale'")
    print("- 'What gaming consoles do you have?'")
    print("\nType 'exit' to quit\n")
    
    chat_history = []
    
    while True:
        try:
            query = input("You: ").strip()
            if not query:
                continue
                
            if query.lower() in ["exit", "quit", "bye"]:
                print("Assistant: Thank you for using VibeShop! Have a great day! 🛍️")
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