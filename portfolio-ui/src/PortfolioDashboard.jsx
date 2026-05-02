import React, { useState, useEffect } from 'react';
import styles from './PortfolioDashboard.module.css';
import DashboardPage from './components/DashboardPage';
import PortfolioPage from './components/PortfolioPage';
import AnalyticsPage from './components/AnalyticsPage';
import ChatPage from './components/ChatPage';
import { checkHealth } from './api';

const PAGES = ['Dashboard', 'Portfolio', 'Analytics', 'Chat'];

const PortfolioDashboard = () => {
    const [activePage, setActivePage] = useState('Dashboard');
    const [userId, setUserId] = useState('hardcoded_user_1');
    const [editingUserId, setEditingUserId] = useState(false);
    const [currentTime, setCurrentTime] = useState(new Date());
    const [backendStatus, setBackendStatus] = useState('checking');

    useEffect(() => {
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    // Check backend health on mount and every 30s
    useEffect(() => {
        const check = async () => {
            try {
                await checkHealth();
                setBackendStatus('online');
            } catch {
                setBackendStatus('offline');
            }
        };
        check();
        const interval = setInterval(check, 30000);
        return () => clearInterval(interval);
    }, []);

    const renderPage = () => {
        switch (activePage) {
            case 'Portfolio': return <PortfolioPage userId={userId} />;
            case 'Analytics': return <AnalyticsPage />;
            case 'Chat': return <ChatPage userId={userId} />;
            default: return <DashboardPage userId={userId} />;
        }
    };

    return (
        <div className={styles.page}>
            {/* Floating animated orbs */}
            <div className={`${styles.orb} ${styles.orb1}`}></div>
            <div className={`${styles.orb} ${styles.orb2}`}></div>
            <div className={`${styles.orb} ${styles.orb3}`}></div>

            <div className={styles.container}>
                {/* Top Navigation */}
                <div className={styles.topBar}>
                    <div className={styles.logoSection}>
                        <div className={styles.logoIcon}>T</div>
                        <div>
                            <div className={styles.logoText}>Tiser</div>
                            <div className={styles.logoSubtext}>Portfolio Intelligence</div>
                        </div>
                    </div>

                    <div className={styles.navPills}>
                        {PAGES.map((page) => (
                            <button
                                key={page}
                                className={`${styles.navPill} ${activePage === page ? styles.navPillActive : ''}`}
                                onClick={() => setActivePage(page)}
                            >
                                {page}
                            </button>
                        ))}
                    </div>

                    <div className={styles.statusBadge} style={{
                        background: backendStatus === 'online' ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
                        borderColor: backendStatus === 'online' ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)',
                        color: backendStatus === 'online' ? '#10b981' : '#ef4444',
                    }}>
                        <span className={styles.statusDot} style={{
                            background: backendStatus === 'online' ? '#10b981' : '#ef4444',
                        }}></span>
                        {backendStatus === 'online' ? 'Live' : 'Backend Offline'} · {currentTime.toLocaleTimeString()}
                    </div>
                </div>

                {/* User ID selector */}
                <div style={{
                    display: 'flex', alignItems: 'center', gap: '0.75rem',
                    marginBottom: '1.5rem', fontSize: '0.85rem', color: '#94a3b8'
                }}>
                    <span>User:</span>
                    {editingUserId ? (
                        <input
                            className={styles.inputField}
                            style={{ padding: '0.4rem 0.75rem', fontSize: '0.85rem', width: '200px' }}
                            value={userId}
                            onChange={(e) => setUserId(e.target.value)}
                            onBlur={() => setEditingUserId(false)}
                            onKeyDown={(e) => e.key === 'Enter' && setEditingUserId(false)}
                            autoFocus
                        />
                    ) : (
                        <span
                            onClick={() => setEditingUserId(true)}
                            style={{
                                color: '#22d3ee', cursor: 'pointer', fontFamily: "'JetBrains Mono', monospace",
                                borderBottom: '1px dashed rgba(34,211,238,0.3)', paddingBottom: '1px'
                            }}
                        >
                            {userId}
                        </span>
                    )}
                    <span style={{ fontSize: '0.7rem', color: '#64748b' }}>(click to change)</span>
                </div>

                {/* Active Page */}
                {renderPage()}

                {/* Footer */}
                <div className={styles.footer}>
                    <div className={styles.footerLinks}>
                        <a href="#" className={styles.footerLink}>Documentation</a>
                        <a href="#" className={styles.footerLink}>API</a>
                        <a href="#" className={styles.footerLink}>GitHub</a>
                        <a href="#" className={styles.footerLink}>Support</a>
                    </div>
                    <div>Tiser © {new Date().getFullYear()} · Built with LangGraph + Cohere + MongoDB Atlas</div>
                </div>
            </div>
        </div>
    );
};

export default PortfolioDashboard;