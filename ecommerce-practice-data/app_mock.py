import streamlit as st
import time
import os
from enhanced_assistant_mock import MockEnhancedAssistant

# Page Config
st.set_page_config(
    page_title="VibeShop AI Assistant - Mock Demo",
    page_icon="🛍️",
    layout="centered"
)

# Header
st.title("🛍️ VibeShop AI Assistant")
st.markdown("**🤖 Mock Demo - No API Calls Required!**")
st.markdown("**Enhanced with Hybrid Chunking & Smart Search**")
st.markdown("Test the enhanced system without API limits!")

# Sidebar with sample queries
with st.sidebar:
    st.header("💡 Try These Queries")
    sample_queries = [
        "Show me gaming laptops under $2000",
        "What's the best Titan laptop?",
        "Compare smartphone cameras",
        "What's your return policy?",
        "Show me products on sale",
        "What headphones do you recommend?",
        "Tell me about warranty coverage",
        "Show me Apex smartphones",
        "What gaming consoles are available?",
        "Find kitchen appliances under $500"
    ]
    
    for query in sample_queries:
        if st.button(query, key=f"sample_{hash(query)}"):
            st.session_state.sample_query = query
    
    st.markdown("---")
    st.markdown("**🤖 Mock Demo Features:**")
    st.markdown("• ✅ Real Vector Database")
    st.markdown("• ✅ Hybrid Chunking")
    st.markdown("• ✅ Smart Filtering")
    st.markdown("• ✅ Boosted Retrieval")
    st.markdown("• 🚫 No API Calls")
    
    st.markdown("---")
    st.markdown("**📊 System Info:**")
    st.markdown("• 500+ Products")
    st.markdown("• 3,071 Smart Chunks")
    st.markdown("• 5 Categories")
    st.markdown("• 22 Brands")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize Mock Enhanced Assistant (Cache Resource to avoid reloading DB on every interaction)
@st.cache_resource
def load_mock_enhanced_assistant():
    try:
        return MockEnhancedAssistant()
    except Exception as e:
        st.error(f"Failed to initialize Mock Enhanced Assistant: {e}")
        return None

assistant = load_mock_enhanced_assistant()

if not assistant:
    st.error("❌ Failed to initialize the Mock Enhanced AI Assistant. Please check:")
    st.markdown("- Vector database exists (run enhanced_index_documents.py)")
    st.markdown("- All required packages are installed")
    st.stop()
else:
    st.success("✅ Mock Enhanced Assistant loaded successfully! 🤖")

# Handle sample query from sidebar
if hasattr(st.session_state, 'sample_query'):
    prompt = st.session_state.sample_query
    del st.session_state.sample_query
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Construct chat history
        chat_history_str = "\n".join(
            [f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages[:-1]]
        )
        
        try:
            with st.spinner("🔍 Searching enhanced database with hybrid chunking..."):
                response = assistant.query(prompt, chat_history_str)
            
            # Stream effect
            full_response = ""
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.005)  # Very fast streaming for demo
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            full_response = f"⚠️ Mock Assistant Error: {str(e)}"
            message_placeholder.error(full_response)
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("How can I help you today?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Assistant Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Construct chat history string for the enhanced assistant
        chat_history_str = "\n".join(
            [f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages[:-1]]
        )
        
        try:
            # Show enhanced spinner
            with st.spinner("🤖 Processing with Mock Enhanced Assistant..."):
                # Use the mock enhanced assistant
                response = assistant.query(prompt, chat_history_str)
            
            # Simulate stream effect with very fast typing for demo
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.005)  # Very fast for demo
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            full_response = f"⚠️ Mock Assistant encountered an error: {str(e)}"
            message_placeholder.error(full_response)
        
    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Footer with system info
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Products", "500+")
with col2:
    st.metric("Smart Chunks", "3,071")
with col3:
    st.metric("Categories", "5")
with col4:
    st.metric("API Calls", "0 🤖")

# Demo info
with st.expander("ℹ️ About This Mock Demo"):
    st.markdown("""
    **🤖 This is a Mock Demo Version**
    
    This version demonstrates the full hybrid chunking system without making API calls:
    
    **✅ What Works:**
    - Real vector database with 3,071 chunks
    - Smart query analysis and filter extraction
    - Metadata filtering (price, category, brand, stock)
    - Boosted retrieval with summary prioritization
    - Realistic product recommendations
    
    **🤖 What's Mocked:**
    - LLM responses (uses templates + retrieved data)
    - No actual API calls to Google Gemini
    - Responses are generated from retrieved chunks
    
    **🎯 Perfect For:**
    - Testing the hybrid chunking system
    - Demonstrating search capabilities
    - Showing metadata filtering in action
    - Avoiding API rate limits
    
    **To use the real version:** Use `app.py` with a valid Google API key.
    """)