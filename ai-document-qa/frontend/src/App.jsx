import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './index.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatWindowRef = useRef(null);

  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/ask`, {
        question: input,
      });

      const aiMessage = {
        role: 'ai',
        content: response.data.answer,
        sources: response.data.sources,
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error calling API:', error);
      const errorMessage = {
        role: 'ai',
        content: 'I encountered an error. Please ensure the backend and Ollama are running.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = async () => {
    if (window.confirm("Are you sure you want to clear the conversation history?")) {
      try {
        await axios.post(`${API_BASE_URL}/reset`);
        setMessages([]);
      } catch (error) {
        console.error('Error resetting chat:', error);
        alert("Failed to clear history on the server.");
      }
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <div className="logo">🌐</div>
        <h1>AI Digital Assistant</h1>
        <div className="status-badge" style={{ background: 'rgba(99, 102, 241, 0.2)', color: '#818cf8', borderColor: 'rgba(99, 102, 241, 0.3)' }}>
          Digital Skills Active
        </div>
        <button
          onClick={handleClearChat}
          className="clear-btn"
          title="Reset Conversation"
        >
          🗑️ Clear Chat
        </button>
      </header>

      <div className="chat-window" ref={chatWindowRef}>
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <h2>I have Digital Skills! 🌐</h2>
            <p>
              I can now search your <strong>Local Documents</strong> or the <strong>Live Internet</strong> to find the answers you need.
            </p>
            <div style={{ marginTop: '2rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap', justifyContent: 'center' }}>
              <span className="source-tag">🔍 Local Docs</span>
              <span className="source-tag">🌍 Web Search</span>
              <span className="source-tag">🧠 Session Memory</span>
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <div className="content">{msg.content}</div>
              {msg.sources && msg.sources.length > 0 && (
                <div className="sources">
                  <strong>References:</strong>
                  <div>
                    {msg.sources.map((src, idx) => (
                      <span key={idx} className="source-tag">
                        {src.source} (p. {src.page})
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
        {isLoading && (
          <div className="message ai">
            <div className="loading-dots">
              <div className="dot"></div>
              <div className="dot"></div>
              <div className="dot"></div>
            </div>
          </div>
        )}
      </div>

      <footer className="input-container">
        <form onSubmit={handleSend} className="input-wrapper">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !input.trim()}>
            {isLoading ? '...' : 'Send'}
          </button>
        </form>
      </footer>
    </div>
  );
}

export default App;
