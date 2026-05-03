"""Premium CSS styles for the Nexus Pricing Intelligence Dashboard."""

PREMIUM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root Variables ── */
:root {
    --bg-primary: #06080f;
    --bg-secondary: #0c1120;
    --bg-card: rgba(15, 23, 42, 0.6);
    --border: rgba(99, 179, 237, 0.08);
    --border-hover: rgba(99, 179, 237, 0.2);
    --accent-cyan: #22d3ee;
    --accent-blue: #3b82f6;
    --accent-purple: #a78bfa;
    --accent-green: #34d399;
    --accent-amber: #fbbf24;
    --accent-rose: #fb7185;
    --text-primary: #f1f5f9;
    --text-secondary: rgba(203, 213, 225, 0.7);
    --text-muted: rgba(148, 163, 184, 0.5);
    --glow-cyan: 0 0 20px rgba(34, 211, 238, 0.15);
    --glow-blue: 0 0 20px rgba(59, 130, 246, 0.15);
}

/* ── Global ── */
.main { background: var(--bg-primary) !important; }

.stApp {
    font-family: 'Inter', -apple-system, sans-serif !important;
    background: linear-gradient(145deg, #06080f 0%, #0c1120 40%, #111827 100%) !important;
    color: var(--text-primary) !important;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* ── Animations ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 8px rgba(34, 211, 238, 0.1); }
    50% { box-shadow: 0 0 20px rgba(34, 211, 238, 0.25); }
}
@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
@keyframes live-pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}
@keyframes gradient-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ── Sidebar ── */
div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080c18 0%, #0c1120 50%, #0f172a 100%) !important;
    border-right: 1px solid var(--border) !important;
}
div[data-testid="stSidebar"] .stRadio label {
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    padding: 6px 12px !important;
    border-radius: 8px !important;
}
div[data-testid="stSidebar"] .stRadio label:hover {
    color: var(--accent-cyan) !important;
    background: rgba(34, 211, 238, 0.05) !important;
}

/* ── Header ── */
.hero-header {
    text-align: center;
    padding: 24px 0 8px;
    animation: fadeInUp 0.6s ease-out;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #22d3ee, #3b82f6, #a78bfa);
    background-size: 200% 200%;
    animation: gradient-shift 4s ease infinite;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}
.hero-subtitle {
    font-size: 0.95rem;
    color: var(--text-muted);
    letter-spacing: 0.5px;
}
.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(34, 211, 238, 0.08);
    border: 1px solid rgba(34, 211, 238, 0.2);
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--accent-cyan);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 8px;
}
.live-dot {
    width: 6px; height: 6px;
    background: var(--accent-cyan);
    border-radius: 50%;
    animation: live-pulse 1.5s ease-in-out infinite;
}

/* ── Metric Cards ── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 22px 24px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeInUp 0.5s ease-out;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
    opacity: 0;
    transition: opacity 0.3s;
}
.metric-card:hover {
    transform: translateY(-3px);
    border-color: var(--border-hover);
    box-shadow: var(--glow-cyan);
}
.metric-card:hover::before { opacity: 1; }

.metric-icon {
    font-size: 1.5rem;
    margin-bottom: 8px;
    display: block;
}
.metric-label {
    font-size: 0.7rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1.8px;
    font-weight: 600;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 2rem;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    background: linear-gradient(135deg, #f1f5f9, #cbd5e1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
}
.metric-value.cyan {
    background: linear-gradient(135deg, #22d3ee, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-value.green {
    background: linear-gradient(135deg, #34d399, #10b981);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-value.amber {
    background: linear-gradient(135deg, #fbbf24, #f59e0b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-value.rose {
    background: linear-gradient(135deg, #fb7185, #f43f5e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-delta {
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 6px;
    display: flex;
    align-items: center;
    gap: 4px;
}
.metric-delta.up { color: var(--accent-green); }
.metric-delta.down { color: var(--accent-rose); }

/* ── Section Headers ── */
.section-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    padding-bottom: 10px;
    margin: 28px 0 16px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 10px;
    animation: fadeInUp 0.5s ease-out;
}
.section-header .icon {
    font-size: 1.2rem;
}
.section-tag {
    font-size: 0.65rem;
    background: rgba(59, 130, 246, 0.1);
    color: var(--accent-blue);
    padding: 2px 10px;
    border-radius: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-left: auto;
}

/* ── Chart Container ── */
.chart-container {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px;
    backdrop-filter: blur(12px);
    animation: fadeInUp 0.6s ease-out;
    transition: border-color 0.3s;
}
.chart-container:hover {
    border-color: var(--border-hover);
}

/* ── Info Badge ── */
.info-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.75rem;
    color: var(--text-muted);
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border);
    padding: 4px 12px;
    border-radius: 8px;
    margin-bottom: 12px;
}

/* ── Page Title ── */
.page-title {
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -0.3px;
    background: linear-gradient(135deg, #f1f5f9, #94a3b8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
    animation: fadeInUp 0.4s ease-out;
}
.page-desc {
    color: var(--text-muted);
    font-size: 0.9rem;
    margin-bottom: 20px;
    animation: fadeInUp 0.5s ease-out;
}

/* ── Footer ── */
.footer {
    text-align: center;
    padding: 32px 0 16px;
    color: var(--text-muted);
    font-size: 0.7rem;
    letter-spacing: 0.5px;
    border-top: 1px solid var(--border);
    margin-top: 48px;
}

/* ── Streamlit Overrides ── */
.stSelectbox label, .stTextInput label, .stNumberInput label, .stSlider label, .stDateInput label {
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
}
button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue)) !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
}
.stDataFrame { border-radius: 12px !important; overflow: hidden; }
h1, h2, h3 { color: var(--text-primary) !important; }
.stMarkdown p { color: var(--text-secondary); }
.stDivider { border-color: var(--border) !important; }
</style>
"""
