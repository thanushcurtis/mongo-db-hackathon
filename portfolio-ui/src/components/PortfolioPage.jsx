import React, { useState, useEffect } from 'react';
import styles from '../PortfolioDashboard.module.css';
import { fetchPortfolio } from '../api';

const FALLBACK_COLORS = ['#6366f1', '#a855f7', '#22d3ee', '#10b981', '#f59e0b', '#ef4444', '#ec4899'];

const PortfolioPage = ({ userId }) => {
    const [holdings, setHoldings] = useState([]);
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            try {
                const data = await fetchPortfolio(userId);
                setProfile(data);
                setHoldings(data.portfolio || []);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [userId]);

    if (loading) {
        return (
            <div className={styles.sectionCard} style={{ textAlign: 'center', padding: '3rem' }}>
                <div className={styles.spinnerContainer}><div className={styles.spinner}></div></div>
                <p style={{ color: '#94a3b8' }}>Loading portfolio...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className={styles.sectionCard} style={{ borderColor: 'rgba(239,68,68,0.3)' }}>
                <div className={styles.sectionTitle} style={{ color: '#ef4444' }}>Error Loading Portfolio</div>
                <p style={{ color: '#94a3b8' }}>{error}</p>
                <p style={{ color: '#64748b', fontSize: '0.8rem', marginTop: '0.5rem' }}>
                    Make sure the backend is running and user <strong>{userId}</strong> exists in MongoDB.
                </p>
            </div>
        );
    }

    return (
        <>
            {/* Profile info */}
            {profile && (
                <div className={styles.statsRow}>
                    <div className={styles.statCard}>
                        <div className={styles.statLabel}>Investor</div>
                        <div className={styles.statValue} style={{ fontSize: '1.4rem' }}>{profile.name || userId}</div>
                    </div>
                    <div className={styles.statCard}>
                        <div className={styles.statLabel}>Risk Profile</div>
                        <div className={styles.statValue} style={{ fontSize: '1.4rem', color: '#f59e0b', textTransform: 'capitalize' }}>
                            {profile.risk_tolerance || 'moderate'}
                        </div>
                    </div>
                    <div className={styles.statCard}>
                        <div className={styles.statLabel}>Holdings</div>
                        <div className={styles.statValue}>{holdings.length}</div>
                    </div>
                    <div className={styles.statCard}>
                        <div className={styles.statLabel}>User ID</div>
                        <div className={styles.statValue} style={{ fontSize: '1rem', fontFamily: "'JetBrains Mono', monospace" }}>{userId}</div>
                    </div>
                </div>
            )}

            {/* Holdings table */}
            <div className={styles.sectionCard}>
                <div className={styles.sectionTitle}>Your Holdings</div>
                {holdings.length === 0 ? (
                    <p style={{ color: '#64748b', textAlign: 'center', padding: '2rem' }}>No holdings found for this user.</p>
                ) : (
                    <table className={styles.holdingsTable}>
                        <thead>
                            <tr>
                                <th>Asset</th>
                                <th>Shares</th>
                                <th>Buy Price</th>
                            </tr>
                        </thead>
                        <tbody>
                            {holdings.map((h, i) => (
                                <tr key={h.ticker}>
                                    <td>
                                        <div className={styles.tickerCell}>
                                            <div className={styles.tickerIcon}
                                                style={{ background: FALLBACK_COLORS[i % FALLBACK_COLORS.length] }}>
                                                {h.ticker.slice(0, 2)}
                                            </div>
                                            <div>
                                                <div className={styles.tickerName}>{h.ticker}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td>{h.shares}</td>
                                    <td>${h.buy_price?.toFixed(2) ?? 'N/A'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </>
    );
};

export default PortfolioPage;
