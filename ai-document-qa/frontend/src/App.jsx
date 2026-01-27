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
    // Scroll to bottom whenever messages change
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
        content: 'Sorry, I encountered an error. Please make sure the backend is running.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <div className="logo">🧠</div>
        <h1>AI Document Agent</h1>
        <div className="status-badge">Active</div>
        <div style={{ marginLeft: 'auto', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
          Free & Local
        </div>
      </header>

      <div className="chat-window" ref={chatWindowRef}>
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <h2>Hello! 👋</h2>
            <p>
              I'm your private AI assistant. Ask me anything about your business
              documents and I'll find the answer for you.
            </p>
            <div style={{ marginTop: '2rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap', justifyContent: 'center' }}>
               <span className="source-tag">Company Policy</span>
               <span className="source-tag">Project Updates</span>
               <span className="source-tag">Service List</span>
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <div className="content">{msg.content}</div>
              {msg.sources && msg.sources.length > 0 && (
                <div className="sources">
                  <strong>Sources:</strong>
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
            placeholder="Ask a question..."
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
