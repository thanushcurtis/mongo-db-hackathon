import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import styles from '../PortfolioDashboard.module.css';
import { sendChatMessage } from '../api';
import { MessageSquare, Plus, Clock, Trash2 } from 'lucide-react';

const INITIAL_MESSAGES = [
    { role: 'bot', text: 'Welcome to Tiser AI Chat. Ask me anything about your portfolio, market trends, or specific stocks. I will answer based on your profile.' },
];

const ChatPage = ({ userId }) => {
    const [sessions, setSessions] = useState([]);
    const [activeChatId, setActiveChatId] = useState(null);
    const [messages, setMessages] = useState(INITIAL_MESSAGES);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);

    // Load sessions from localStorage
    useEffect(() => {
        const saved = localStorage.getItem(`tiser_chats_${userId}`);
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                setSessions(parsed);
                if (parsed.length > 0) {
                    setActiveChatId(parsed[0].id);
                    setMessages(parsed[0].messages);
                }
            } catch (e) { console.error("Failed to parse chats", e); }
        } else {
            startNewChat();
        }
    }, [userId]);

    // Save sessions to localStorage whenever they change
    useEffect(() => {
        if (sessions.length > 0) {
            localStorage.setItem(`tiser_chats_${userId}`, JSON.stringify(sessions));
        }
    }, [sessions, userId]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => { scrollToBottom(); }, [messages, isTyping]);

    const handleSend = async () => {
        if (!input.trim() || isTyping) return;
        
        const userText = input;
        const newMessages = [...messages, { role: 'user', text: userText }];
        
        setMessages(newMessages);
        setInput('');
        setIsTyping(true);

        // Update session title if it's the first user message
        let currentSessions = [...sessions];
        let sessionIndex = currentSessions.findIndex(s => s.id === activeChatId);
        
        if (sessionIndex !== -1 && currentSessions[sessionIndex].messages.length <= 1) {
            currentSessions[sessionIndex].title = userText.substring(0, 25) + (userText.length > 25 ? '...' : '');
            currentSessions[sessionIndex].date = new Date().toLocaleDateString();
            setSessions(currentSessions);
        }

        try {
            // Strip out introductory bot message and pass history
            const history = newMessages.slice(1, -1).map(m => ({ role: m.role, text: m.text }));
            const data = await sendChatMessage(userId, userText, history);
            
            const finalMessages = [...newMessages, { role: 'bot', text: data.report, isMarkdown: true }];
            setMessages(finalMessages);
            
            // Save to current session
            const updatedSessions = [...sessions];
            const idx = updatedSessions.findIndex(s => s.id === activeChatId);
            if (idx !== -1) {
                updatedSessions[idx].messages = finalMessages;
                setSessions(updatedSessions);
            }
        } catch (err) {
            setMessages(prev => [...prev, {
                role: 'bot',
                text: `Error: ${err.message}. Make sure the backend is running.`
            }]);
        } finally {
            setIsTyping(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const startNewChat = () => {
        const newId = Date.now().toString();
        const newSession = {
            id: newId,
            title: 'New Conversation',
            date: new Date().toLocaleDateString(),
            messages: INITIAL_MESSAGES
        };
        setSessions([newSession, ...sessions]);
        setActiveChatId(newId);
        setMessages(INITIAL_MESSAGES);
    };

    const switchChat = (id) => {
        const session = sessions.find(s => s.id === id);
        if (session) {
            setActiveChatId(id);
            setMessages(session.messages);
        }
    };
    
    const deleteChat = (e, id) => {
        e.stopPropagation();
        const updated = sessions.filter(s => s.id !== id);
        setSessions(updated);
        if (updated.length === 0) {
            startNewChat();
        } else if (activeChatId === id) {
            setActiveChatId(updated[0].id);
            setMessages(updated[0].messages);
        }
        if (updated.length === 0) {
            localStorage.removeItem(`tiser_chats_${userId}`);
        }
    };

    return (
        <div style={{ display: 'flex', height: 'calc(100vh - 200px)', gap: '1.5rem', width: '100%' }}>
            {/* Sidebar for Past Chats */}
            <div style={{ 
                width: '280px', 
                background: 'var(--bg-glass)', 
                backdropFilter: 'blur(20px)',
                border: '1px solid var(--border-glass)', 
                borderRadius: 'var(--radius)', 
                padding: '1.25rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '1rem',
                overflowY: 'auto'
            }}>
                <button 
                    onClick={startNewChat}
                    style={{
                        display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.85rem',
                        background: 'rgba(99, 102, 241, 0.1)', color: 'var(--accent-blue)',
                        border: '1px solid rgba(99, 102, 241, 0.2)', borderRadius: '8px',
                        cursor: 'pointer', fontWeight: 600, transition: 'all 0.2s', width: '100%',
                        justifyContent: 'center'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(99, 102, 241, 0.2)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(99, 102, 241, 0.1)'}
                >
                    <Plus size={18} /> New Chat
                </button>
                
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginTop: '0.5rem' }}>
                    <Clock size={12} style={{ display: 'inline', marginRight: '4px' }}/> Recent Sessions
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {sessions.map((chat) => (
                        <div key={chat.id} 
                            onClick={() => switchChat(chat.id)}
                            style={{
                            padding: '0.85rem',
                            background: activeChatId === chat.id ? 'rgba(255,255,255,0.08)' : 'transparent',
                            border: '1px solid',
                            borderColor: activeChatId === chat.id ? 'rgba(255,255,255,0.1)' : 'transparent',
                            borderRadius: '8px', cursor: 'pointer', transition: 'all 0.2s',
                            display: 'flex', flexDirection: 'column', gap: '0.25rem',
                            position: 'relative'
                        }}
                        onMouseEnter={(e) => {
                            if (activeChatId !== chat.id) e.currentTarget.style.background = 'rgba(255,255,255,0.03)';
                            e.currentTarget.querySelector('.del-btn').style.opacity = 1;
                        }}
                        onMouseLeave={(e) => {
                            if (activeChatId !== chat.id) e.currentTarget.style.background = 'transparent';
                            e.currentTarget.querySelector('.del-btn').style.opacity = 0;
                        }}
                        >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-primary)', fontSize: '0.9rem', fontWeight: 500, paddingRight: '1rem' }}>
                                <MessageSquare size={14} color="var(--accent-cyan)" />
                                <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{chat.title}</span>
                            </div>
                            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', paddingLeft: '1.3rem' }}>{chat.date}</div>
                            
                            <div className="del-btn" 
                                 onClick={(e) => deleteChat(e, chat.id)}
                                 style={{ position: 'absolute', right: '0.5rem', top: '0.85rem', opacity: 0, transition: 'opacity 0.2s', color: 'var(--accent-red)' }}>
                                <Trash2 size={14} />
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Main Chat Area */}
            <div className={styles.chatContainer} style={{ flex: 1, height: '100%', margin: 0 }}>
                <div className={styles.chatMessages}>
                    {messages.map((msg, i) => (
                        <div key={i} className={`${styles.chatBubble} ${msg.role === 'user' ? styles.chatUser : styles.chatBot}`}>
                            {msg.role === 'bot' && <div className={styles.chatBotLabel}>Tiser AI</div>}
                            {msg.isMarkdown ? (
                                <div className={styles.reportContent}><ReactMarkdown>{msg.text}</ReactMarkdown></div>
                            ) : (
                                msg.text
                            )}
                        </div>
                    ))}
                    {isTyping && (
                        <div className={`${styles.chatBubble} ${styles.chatBot}`}>
                            <div className={styles.chatBotLabel}>Tiser AI</div>
                            <div className={styles.chatTyping}>
                                <span></span><span></span><span></span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
                <div className={styles.chatInputRow}>
                    <input
                        className={styles.chatInput}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask about your portfolio, market trends, or any stock..."
                        disabled={isTyping}
                    />
                    <button className={styles.chatSend} onClick={handleSend} disabled={isTyping || !input.trim()}>
                        {isTyping ? 'Thinking...' : 'Send →'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ChatPage;
