import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import styles from './PortfolioDashboard.module.css';

const PortfolioDashboard = () => {
    const [userId, setUserId] = useState('user_123');
    const [chatMessage, setChatMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [step, setStep] = useState('');
    const [pipelinePhase, setPipelinePhase] = useState(0); // 0=idle,1=manager,2=research,3=trend,4=synth
    const [report, setReport] = useState(null);
    const [currentTime, setCurrentTime] = useState(new Date());

    useEffect(() => {
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    const handleRunAnalysis = async () => {
        if (!userId.trim()) return;

        setLoading(true);
        setReport(null);
        setPipelinePhase(1);
        setStep('Manager Agent: Reading user profile...');

        try {
            /*
            const response = await fetch('/api/portfolio/analyze', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ user_id: userId, chat_message: chatMessage })
            });
            const data = await response.json();
            setReport(data.final_report);
            */

            // --- SIMULATION FOR UI DEMO ---
            setTimeout(() => {
                setPipelinePhase(2);
                setStep('Research Agent: Fetching news & RAG sentiment analysis...');
            }, 1500);
            setTimeout(() => {
                setPipelinePhase(3);
                setStep('Trend Agent: Analyzing moving averages & market signals...');
            }, 3500);
            setTimeout(() => {
                setPipelinePhase(4);
                setStep('Synthesizer: Generating personalized Markdown report...');
            }, 5500);
            setTimeout(() => {
                setReport(mockMarkdownReport);
                setLoading(false);
                setPipelinePhase(0);
            }, 7500);
        } catch (error) {
            console.error("Analysis failed:", error);
            setStep('Error generating report.');
            setLoading(false);
            setPipelinePhase(0);
        }
    };

    const pipelineSteps = [
        { label: 'Manager', phase: 1 },
        { label: 'Research', phase: 2 },
        { label: 'Trends', phase: 3 },
        { label: 'Synthesize', phase: 4 },
    ];

    return (
        <div className={styles.page}>
            <div className={styles.container}>
                {/* ── Top Navigation ── */}
                <div className={styles.topBar}>
                    <div className={styles.logoSection}>
                        <div className={styles.logoIcon}>📈</div>
                        <div>
                            <div className={styles.logoText}>TradeHub</div>
                            <div className={styles.logoSubtext}>Portfolio Intelligence</div>
                        </div>
                    </div>

                    <div className={styles.navPills}>
                        <button className={`${styles.navPill} ${styles.navPillActive}`}>Dashboard</button>
                        <button className={styles.navPill}>Portfolio</button>
                        <button className={styles.navPill}>Analytics</button>
                        <button className={styles.navPill}>Settings</button>
                    </div>

                    <div className={styles.statusBadge}>
                        <span className={styles.statusDot}></span>
                        Live · {currentTime.toLocaleTimeString()}
                    </div>
                </div>

                {/* ── Hero Section ── */}
                <div className={styles.hero}>
                    <h1 className={styles.heroTitle}>
                        AI-Powered <span className={styles.heroGradient}>Portfolio Analysis</span>
                    </h1>
                    <p className={styles.heroSubtitle}>
                        Multi-agent orchestration with LangGraph, Cohere AI, and MongoDB Atlas
                        Vector Search — delivering institutional-grade insights in seconds.
                    </p>
                    <div className={styles.heroBadges}>
                        <span className={styles.heroBadge}><span>🤖</span> Cohere Command-A</span>
                        <span className={styles.heroBadge}><span>🧠</span> Voyage AI Embeddings</span>
                        <span className={styles.heroBadge}><span>🍃</span> MongoDB Atlas</span>
                        <span className={styles.heroBadge}><span>🔗</span> LangGraph</span>
                    </div>
                </div>

                {/* ── Stats Row ── */}
                <div className={styles.statsRow}>
                    <div className={styles.statCard}>
                        <div className={styles.statLabel}>Portfolio Value</div>
                        <div className={styles.statValue}>$48,250</div>
                        <span className={`${styles.statChange} ${styles.statUp}`}>↑ +12.4%</span>
                    </div>
                    <div className={styles.statCard}>
                        <div className={styles.statLabel}>Today's P&L</div>
                        <div className={styles.statValue} style={{ color: '#10b981' }}>+$1,240</div>
                        <span className={`${styles.statChange} ${styles.statUp}`}>↑ +2.6%</span>
                    </div>
                    <div className={styles.statCard}>
                        <div className={styles.statLabel}>Active Positions</div>
                        <div className={styles.statValue}>7</div>
                        <span className={`${styles.statChange} ${styles.statDown}`}>↓ -1 closed</span>
                    </div>
                    <div className={styles.statCard}>
                        <div className={styles.statLabel}>Risk Score</div>
                        <div className={styles.statValue} style={{ color: '#f59e0b' }}>6.2</div>
                        <span className={`${styles.statChange} ${styles.statUp}`}>Moderate</span>
                    </div>
                </div>

                {/* ── Control Panel ── */}
                <div className={styles.controlPanel}>
                    <div className={styles.controlTitle}>
                        ⚡ Analysis Engine
                    </div>
                    <div className={styles.controlGrid}>
                        <div className={styles.inputGroup}>
                            <label className={styles.inputLabel} htmlFor="userId">User ID</label>
                            <input
                                id="userId"
                                type="text"
                                className={styles.inputField}
                                value={userId}
                                onChange={(e) => setUserId(e.target.value)}
                                placeholder="e.g. user_123"
                            />
                        </div>
                        <div className={styles.inputGroup}>
                            <label className={styles.inputLabel} htmlFor="chatMessage">Ask a Question (Optional)</label>
                            <input
                                id="chatMessage"
                                type="text"
                                className={styles.inputField}
                                value={chatMessage}
                                onChange={(e) => setChatMessage(e.target.value)}
                                placeholder="e.g. Should I rebalance my tech-heavy portfolio?"
                            />
                        </div>
                        <button
                            className={styles.runButton}
                            onClick={handleRunAnalysis}
                            disabled={loading}
                        >
                            {loading ? '⏳ Running Graph...' : '🚀 Generate Report'}
                        </button>
                    </div>
                </div>

                {/* ── Loading State ── */}
                {loading && (
                    <div className={styles.loadingCard}>
                        <div className={styles.spinnerContainer}>
                            <div className={styles.spinner}></div>
                        </div>
                        <div className={styles.loadingStep}>{step}</div>
                        <div className={styles.loadingHint}>
                            Multi-agent pipeline in progress — typically 10-15 seconds
                        </div>

                        <div className={styles.pipelineSteps}>
                            {pipelineSteps.map((s) => {
                                let cls = styles.pipelineStep;
                                if (pipelinePhase === s.phase) cls += ` ${styles.pipelineStepActive}`;
                                else if (pipelinePhase > s.phase) cls += ` ${styles.pipelineStepDone}`;
                                return (
                                    <div key={s.phase} className={cls}>
                                        <span className={styles.pipelineDot}></span>
                                        {s.label}
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}

                {/* ── Report ── */}
                {report && !loading && (
                    <div className={styles.reportCard}>
                        <div className={styles.reportHeader}>
                            <div>
                                <strong style={{ fontSize: '1rem' }}>📄 Analysis Report</strong>
                                <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem' }}>
                                    Generated by TradeHub AI Pipeline
                                </div>
                            </div>
                            <div className={styles.reportTimestamp}>
                                {new Date().toLocaleString()}
                            </div>
                        </div>
                        <div className={styles.reportContent}>
                            <ReactMarkdown>{report}</ReactMarkdown>
                        </div>
                    </div>
                )}

                {/* ── Empty State ── */}
                {!report && !loading && (
                    <div className={styles.emptyState}>
                        <div className={styles.emptyIcon}>🔮</div>
                        <div className={styles.emptyTitle}>Ready to Analyze</div>
                        <div className={styles.emptySubtitle}>
                            Enter a user ID and click "Generate Report" to run the multi-agent
                            pipeline and receive your personalized portfolio analysis.
                        </div>
                    </div>
                )}

                {/* ── Footer ── */}
                <div className={styles.footer}>
                    <div className={styles.footerLinks}>
                        <a href="#" className={styles.footerLink}>Documentation</a>
                        <a href="#" className={styles.footerLink}>API</a>
                        <a href="#" className={styles.footerLink}>GitHub</a>
                        <a href="#" className={styles.footerLink}>Support</a>
                    </div>
                    <div>
                        TradeHub © {new Date().getFullYear()} · Built with LangGraph + Cohere + MongoDB Atlas
                    </div>
                </div>
            </div>
        </div>
    );
};

// ── Mock report for UI testing ──────────────────────────────────
const mockMarkdownReport = `
# 📊 Portfolio Analysis Report for Brinda

## Executive Summary
Your portfolio is currently valued at **$48,250**, reflecting a **+12.4% gain** since inception. Overall sentiment is **cautiously bullish** with strong fundamentals across your core holdings. Your moderate risk profile is well-matched to current positions, though slight rebalancing is recommended.

## 📈 Individual Stock Analysis

### AAPL — Apple Inc.
- **Position:** 10 shares @ $150.00 → Current: $198.50
- **P&L:** +$485.00 (+32.3%) 🟢
- **Sentiment:** 🟢 **Bullish**
- **Recommendation:** **HOLD** — Strong hardware cycle ahead with Vision Pro momentum. Institutional confidence remains high based on RAG analysis of 47 recent articles.
- **Key Risk:** Regulatory headwinds in EU markets.

### MSFT — Microsoft Corp.
- **Position:** 5 shares @ $300.00 → Current: $425.80
- **P&L:** +$629.00 (+41.9%) 🟢
- **Sentiment:** 🟢 **Strong Buy**
- **Recommendation:** **BUY MORE** — Azure AI revenue accelerating. Copilot adoption driving enterprise growth. Moving averages signal continued uptrend.
- **Key Risk:** Antitrust scrutiny on Activision integration.

## 📉 Technical Trends

| Ticker | 50-Day MA | 200-Day MA | Signal | RSI |
|--------|-----------|------------|--------|-----|
| AAPL   | $192.40   | $178.20    | 🟢 Golden Cross | 62.4 |
| MSFT   | $418.60   | $385.90    | 🟢 Uptrend | 58.1 |

## 🔥 Market Opportunities
Based on your **moderate** risk profile, consider these trending picks:
1. **NVDA** — AI infrastructure demand surging, 92% buy rating
2. **AMZN** — AWS momentum + retail recovery, strong technicals
3. **GOOGL** — Undervalued relative to AI peers, Gemini catalyst

## 👥 Platform Insights
- **Most held stock** on TradeHub this week: NVDA (held by 78% of users)
- **Trending buy:** PLTR (+340% platform interest this month)
- **Top seller:** TSLA (15% of holders reduced positions)

## ✅ Action Plan
1. **HOLD** current AAPL position — do not sell before Q3 earnings
2. **BUY** 2-3 more shares of MSFT on any dip below $420
3. **RESEARCH** NVDA for a potential 5% portfolio allocation
4. **SET** stop-loss on AAPL at $185 to protect gains
5. **REVIEW** portfolio again in 2 weeks after Fed rate decision
`;

export default PortfolioDashboard;