import React, { useState, useEffect } from 'react';
import styles from '../PortfolioDashboard.module.css';
import { TrendingUp, TrendingDown, Activity, RefreshCw } from 'lucide-react';

const sectorData = [
    { label: 'Tech', value: 65, color: '#6366f1' },
    { label: 'Healthcare', value: 12, color: '#10b981' },
    { label: 'Finance', value: 10, color: '#f59e0b' },
    { label: 'Energy', value: 8, color: '#ef4444' },
    { label: 'Consumer', value: 5, color: '#22d3ee' },
];

const sparklineHeights = [20, 35, 28, 45, 38, 52, 48, 60, 55, 70, 65, 78, 72, 85, 80];

const AnalyticsPage = () => {
    const [hotStocks, setHotStocks] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTrends = async () => {
            try {
                const res = await fetch('http://127.0.0.1:8000/api/market-trends');
                const json = await res.json();
                if (json.data) {
                    setHotStocks(json.data);
                }
            } catch (err) {
                console.error("Failed to fetch market trends:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchTrends();
    }, []);

    // Helper to get color based on change
    const getChangeColor = (change) => change >= 0 ? '#10b981' : '#ef4444';
    const getChangeBg = (change) => change >= 0 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)';

    return (
        <>
            {/* Live Market Trends Widget (Persuasive & Dynamic) */}
            <div className={styles.chartCard} style={{ 
                marginBottom: '1.5rem', 
                background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%)',
                border: '1px solid rgba(99, 102, 241, 0.3)',
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 1px rgba(255,255,255,0.05)',
                position: 'relative',
                overflow: 'hidden'
            }}>
                {/* Glow Effect */}
                <div style={{ position: 'absolute', top: '-50%', left: '-20%', width: '150%', height: '200%', background: 'radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 60%)', pointerEvents: 'none' }}></div>
                
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', position: 'relative', zIndex: 1 }}>
                    <div className={styles.chartTitle} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0, fontSize: '1.1rem', color: '#fff' }}>
                        <Activity size={20} color="#22d3ee" /> Live Market Hot Stocks
                    </div>
                    {loading && <RefreshCw size={16} className={styles.pulseAnimation} color="#94a3b8" />}
                </div>

                {loading ? (
                    <div style={{ padding: '2rem', textAlign: 'center', color: '#94a3b8' }}>Scanning global markets via yfinance...</div>
                ) : (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', position: 'relative', zIndex: 1 }}>
                        {hotStocks.map((stock) => (
                            <div key={stock.ticker} style={{
                                background: 'rgba(255,255,255,0.03)',
                                borderRadius: '12px',
                                padding: '1rem',
                                border: '1px solid rgba(255,255,255,0.05)',
                                display: 'flex',
                                flexDirection: 'column',
                                gap: '0.5rem',
                                transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                                cursor: 'pointer',
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.transform = 'translateY(-3px)';
                                e.currentTarget.style.boxShadow = `0 8px 24px ${getChangeBg(stock.change)}`;
                                e.currentTarget.style.borderColor = getChangeColor(stock.change);
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.transform = 'translateY(0)';
                                e.currentTarget.style.boxShadow = 'none';
                                e.currentTarget.style.borderColor = 'rgba(255,255,255,0.05)';
                            }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span style={{ fontWeight: 700, fontSize: '1.1rem', color: '#f8fafc', letterSpacing: '0.5px' }}>{stock.ticker}</span>
                                    <span style={{ 
                                        padding: '0.2rem 0.5rem', 
                                        borderRadius: '20px', 
                                        fontSize: '0.7rem', 
                                        fontWeight: 600,
                                        background: getChangeBg(stock.change),
                                        color: getChangeColor(stock.change),
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.2rem'
                                    }}>
                                        {stock.change >= 0 ? <TrendingUp size={12}/> : <TrendingDown size={12}/>}
                                        {stock.change > 0 ? '+' : ''}{stock.change.toFixed(2)}%
                                    </span>
                                </div>
                                <div style={{ fontSize: '1.5rem', fontWeight: 300, color: '#f1f5f9', marginTop: '0.25rem' }}>
                                    ${stock.price.toFixed(2)}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className={styles.analyticsGrid}>
                {/* Sector Allocation */}
                <div className={styles.chartCard}>
                    <div className={styles.chartTitle}>Sector Allocation</div>
                    {sectorData.map((s) => (
                        <div key={s.label} style={{ marginBottom: '0.75rem' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.3rem' }}>
                                <span style={{ color: '#94a3b8' }}>{s.label}</span>
                                <span style={{ color: '#f1f5f9', fontWeight: 600 }}>{s.value}%</span>
                            </div>
                            <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                                <div style={{
                                    width: `${s.value}%`, height: '100%', background: s.color,
                                    borderRadius: '3px', transition: 'width 1s ease'
                                }}></div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Portfolio Growth */}
                <div className={styles.chartCard}>
                    <div className={styles.chartTitle}>Portfolio Growth (15 Weeks)</div>
                    <div className={styles.miniSparkline}>
                        {sparklineHeights.map((h, i) => (
                            <span key={i} style={{
                                height: `${h}%`,
                                background: `linear-gradient(180deg, #6366f1, #a855f7)`,
                                opacity: 0.5 + (i / sparklineHeights.length) * 0.5,
                                borderRadius: '3px',
                            }}></span>
                        ))}
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem', fontSize: '0.7rem', color: '#64748b' }}>
                        <span>15 weeks ago</span><span>Today</span>
                    </div>
                </div>
            </div>
        </>
    );
};

export default AnalyticsPage;
