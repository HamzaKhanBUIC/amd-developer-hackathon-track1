"use client";
import { useState, useRef, useEffect } from 'react';
import styles from './ChatInterface.module.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  metadata?: {
    model_selected: string;
    routing_layer: string;
    tokens_saved: number;
  };
}

export default function ChatInterface() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [totalSaved, setTotalSaved] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      // In a real app, this points to our FastAPI backend running on port 8000
      const res = await fetch('http://localhost:8000/api/route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: userMsg.content })
      });
      
      if (!res.ok) throw new Error('API Error');
      const data = await res.json();
      
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        metadata: {
          model_selected: data.model_selected,
          routing_layer: data.routing_layer,
          tokens_saved: data.tokens_saved
        }
      };
      
      setMessages(prev => [...prev, assistantMsg]);
      setTotalSaved(prev => prev + data.tokens_saved);
    } catch (err) {
      console.error(err);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "System error: Unable to reach the Zero-Token Router API. Please ensure the backend is running."
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.brand}>
          <div className={styles.amdLogo}></div>
          <h1>Zero-Token Router</h1>
        </div>
        <div className={styles.metricsBadge}>
          <span>Tokens Saved: <strong>{totalSaved.toLocaleString()}</strong></span>
        </div>
      </header>

      <main className={styles.chatArea}>
        {messages.length === 0 ? (
          <div className={styles.emptyState}>
            <h2>Test the Router Pipeline</h2>
            <p>Send an easy query (math, greeting) to trigger the Semantic Layer, or a complex query to trigger the XGBoost Layer.</p>
          </div>
        ) : (
          <div className={styles.messageList}>
            {messages.map((msg) => (
              <div key={msg.id} className={`${styles.messageWrapper} ${msg.role === 'user' ? styles.userWrapper : styles.assistantWrapper}`}>
                <div className={`${styles.messageBubble} ${msg.role === 'user' ? styles.userBubble : styles.assistantBubble}`}>
                  <p>{msg.content}</p>
                </div>
                
                {msg.metadata && (
                  <div className={styles.metadataPill}>
                    <span className={styles.layerBadge} data-layer={msg.metadata.routing_layer}>
                      {msg.metadata.routing_layer.toUpperCase()} LAYER
                    </span>
                    <span className={styles.modelTag}>{msg.metadata.model_selected.split('/').pop()}</span>
                    {msg.metadata.tokens_saved > 0 && (
                      <span className={styles.savingsTag}>+{msg.metadata.tokens_saved} tokens</span>
                    )}
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className={styles.loadingIndicator}>
                <div className={styles.dot}></div>
                <div className={styles.dot}></div>
                <div className={styles.dot}></div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      <div className={styles.inputArea}>
        <form onSubmit={handleSubmit} className={styles.form}>
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter a prompt to route..."
            className={styles.input}
            disabled={isLoading}
          />
          <button type="submit" className={styles.submitBtn} disabled={!input.trim() || isLoading}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12h14M12 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}
