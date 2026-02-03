import streamlit as st
import time
import os
from enhanced_assistant import EnhancedAssistant

# Page Config
st.set_page_config(
    page_title="VibeShop AI Assistant - Enhanced",
    page_icon="🛍️",
    layout="centered"
)

# Header
st.title("🛍️ VibeShop AI Assistant")
st.markdown("**Enhanced with Hybrid Chunking & Smart Search**")
st.markdown("Ask me about products, policies, or get buying advice!")

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
        "Tell me about warranty coverage"
    ]
    
    for query in sample_queries:
        if st.button(query, key=f"sample_{hash(query)}"):
            st.session_state.sample_query = query
    
    st.markdown("---")
    st.markdown("**System Info:**")
    st.markdown("• 500+ Products")
    st.markdown("• 3,071 Smart Chunks")
    st.markdown("• Hybrid Retrieval")
    st.markdown("• Price & Category Filtering")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize Enhanced Assistant (Cache Resource to avoid reloading DB on every interaction)
@st.cache_resource
def load_enhanced_assistant():
    try:
        return EnhancedAssistant()
    except Exception as e:
        st.error(f"Failed to initialize Enhanced Assistant: {e}")
        return None

assistant = load_enhanced_assistant()

if not assistant:
    st.error("❌ Failed to initialize the Enhanced AI Assistant. Please check:")
    st.markdown("- Google API key is set in .env file")
    st.markdown("- Vector database exists (run enhanced_index_documents.py)")
    st.markdown("- All required packages are installed")
    st.stop()
else:
    st.success("✅ Enhanced Assistant loaded successfully!")

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
            with st.spinner("🔍 Searching enhanced database..."):
                response = assistant.query(prompt, chat_history_str)
            
            # Stream effect
            full_response = ""
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.01)
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            full_response = f"⚠️ I encountered an error: {str(e)}"
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
            with st.spinner("🔍 Searching enhanced database with hybrid chunking..."):
                # Use the enhanced assistant
                response = assistant.query(prompt, chat_history_str)
            
            # Simulate stream effect with faster typing
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.01)  # Faster streaming
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            error_msg = str(e)
            if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
                full_response = "⚠️ I'm experiencing high demand right now. Please wait a moment and try again. The enhanced system is working, but the API has rate limits."
            else:
                full_response = f"⚠️ I encountered an error: {error_msg}"
            message_placeholder.error(full_response)
        
    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Footer with system info
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Products", "500+")
with col2:
    st.metric("Smart Chunks", "3,071")
with col3:
    st.metric("Categories", "5")
