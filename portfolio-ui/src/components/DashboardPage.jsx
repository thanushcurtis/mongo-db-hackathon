import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import styles from '../PortfolioDashboard.module.css';
import { runAnalysis } from '../api';

const DashboardPage = ({ userId }) => {
    const [chatMessage, setChatMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [step, setStep] = useState('');
    const [pipelinePhase, setPipelinePhase] = useState(0);
    const [report, setReport] = useState(null);
    const [error, setError] = useState(null);

    const handleRunAnalysis = async () => {
        if (!userId.trim()) return;
        setLoading(true);
        setReport(null);
        setError(null);
        setPipelinePhase(1);
        setStep('Manager Agent: Reading user profile...');

        // Simulate pipeline progress while waiting for backend
        const t1 = setTimeout(() => { setPipelinePhase(2); setStep('Research Agent: Fetching news & RAG sentiment...'); }, 3000);
        const t2 = setTimeout(() => { setPipelinePhase(3); setStep('Trend Agent: Analyzing moving averages...'); }, 8000);
        const t3 = setTimeout(() => { setPipelinePhase(4); setStep('Synthesizer: Generating Markdown report...'); }, 14000);

        try {
            const data = await runAnalysis(userId);
            clearTimeout(t1); clearTimeout(t2); clearTimeout(t3);
            setReport(data.report);
        } catch (err) {
            clearTimeout(t1); clearTimeout(t2); clearTimeout(t3);
            setError(err.message);
            setStep('Error generating report.');
        } finally {
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
        <>
            {/* Stats Row */}
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

            {/* Control Panel */}
            <div className={styles.controlPanel}>
                <div className={styles.controlTitle}>⚡ Analysis Engine</div>
                <div className={styles.controlGrid}>
                    <div className={styles.inputGroup}>
                        <label className={styles.inputLabel}>User ID</label>
                        <input type="text" className={styles.inputField} value={userId} disabled
                            style={{ opacity: 0.7 }} />
                    </div>
                    <div className={styles.inputGroup}>
                        <label className={styles.inputLabel}>Ask a Question (Optional)</label>
                        <input type="text" className={styles.inputField}
                            value={chatMessage} onChange={(e) => setChatMessage(e.target.value)}
                            placeholder="e.g. Should I rebalance my tech-heavy portfolio?" />
                    </div>
                    <button className={styles.runButton} onClick={handleRunAnalysis} disabled={loading}>
                        {loading ? '⏳ Running Graph...' : '🚀 Generate Report'}
                    </button>
                </div>
            </div>

            {/* Loading */}
            {loading && (
                <div className={styles.loadingCard}>
                    <div className={styles.spinnerContainer}><div className={styles.spinner}></div></div>
                    <div className={styles.loadingStep}>{step}</div>
                    <div className={styles.loadingHint}>Multi-agent pipeline in progress — typically 15-30 seconds</div>
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

            {/* Error */}
            {error && !loading && (
                <div className={styles.sectionCard} style={{ borderColor: 'rgba(239,68,68,0.3)' }}>
                    <div className={styles.sectionTitle} style={{ color: '#ef4444' }}>Error</div>
                    <p style={{ color: '#94a3b8' }}>{error}</p>
                    <p style={{ color: '#64748b', fontSize: '0.8rem', marginTop: '0.5rem' }}>
                        Make sure the FastAPI backend is running: <code style={{ color: '#22d3ee' }}>python main.py</code>
                    </p>
                </div>
            )}

            {/* Report */}
            {report && !loading && (
                <div className={styles.reportCard}>
                    <div className={styles.reportHeader}>
                        <div>
                            <strong style={{ fontSize: '1rem' }}>Analysis Report</strong>
                            <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem' }}>
                                Generated by Tiser AI Pipeline
                            </div>
                        </div>
                        <div className={styles.reportTimestamp}>{new Date().toLocaleString()}</div>
                    </div>
                    <div className={styles.reportContent}><ReactMarkdown>{report}</ReactMarkdown></div>
                </div>
            )}

            {/* Empty state */}
            {!report && !loading && !error && (
                <div className={styles.emptyState}>
                    <div className={styles.emptyTitle}>Ready to Analyze</div>
                    <div className={styles.emptySubtitle}>
                        Click "Generate Report" to run the multi-agent LangGraph pipeline against your portfolio.
                    </div>
                </div>
            )}
        </>
    );
};

export default DashboardPage;
