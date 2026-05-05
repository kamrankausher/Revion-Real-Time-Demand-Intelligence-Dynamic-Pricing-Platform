"""Premium Obsidian Glass Enterprise Design System for Revion Dashboard."""

import streamlit as st

def load_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap');

    /* ── Root Theme Variables (Dark Default) ── */
    :root {
        --bg-base: #09090B;
        --bg-surface: #111113;
        --bg-glass: rgba(255,255,255,0.04);
        --bg-glass-hover: rgba(255,255,255,0.07);
        --border-glass: rgba(255,255,255,0.08);
        --border-glass-bright: rgba(255,255,255,0.15);
        --accent-primary: #6366F1;
        --accent-secondary: #22D3EE;
        --accent-success: #10B981;
        --accent-warning: #F59E0B;
        --accent-danger: #EF4444;
        --accent-purple: #A855F7;
        --text-primary: #FAFAFA;
        --text-secondary: #A1A1AA;
        --text-muted: #52525B;
        --glow-primary: 0 0 40px rgba(99,102,241,0.3);
        --glow-cyan: 0 0 30px rgba(34,211,238,0.2);
        --glow-success: 0 0 20px rgba(16,185,129,0.2);
    }

    /* Light Theme override class (toggled via JS/Streamlit) */
    [data-theme="light"] {
        --bg-base: #F8F9FF;
        --bg-surface: #FFFFFF;
        --bg-glass: rgba(99,102,241,0.04);
        --bg-glass-hover: rgba(99,102,241,0.08);
        --border-glass: rgba(99,102,241,0.12);
        --border-glass-bright: rgba(99,102,241,0.25);
        --accent-primary: #4F46E5;
        --accent-secondary: #0891B2;
        --text-primary: #0A0A0B;
        --text-secondary: #52525B;
        --text-muted: #A1A1AA;
        --glow-primary: 0 0 40px rgba(79,70,229,0.15);
    }

    /* ── Global Styles ── */
    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: var(--bg-base) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        transition: background-color 0.4s ease, color 0.4s ease;
    }

    /* ── Hide Streamlit defaults ── */
    header[data-testid="stHeader"] { background: transparent !important; }
    div[data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }

    /* ── Typography ── */
    h1, h2, h3, h4, h5, h6, .stMarkdown p, .stMarkdown span {
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .kpi-number, code, .stCodeBlock {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* ── Glassmorphism Containers ── */
    .glass-card {
        background: var(--bg-glass);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid var(--border-glass);
        border-radius: 16px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.4), 0 1px 0 rgba(255,255,255,0.05) inset, var(--glow-primary);
        padding: 24px;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        position: relative;
        overflow: hidden;
        animation: slideInUp 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) both;
    }

    .glass-card:hover {
        transform: translateY(-2px) scale(1.005);
        border-color: var(--border-glass-bright);
        box-shadow: 0 8px 40px rgba(0,0,0,0.5), 0 0 50px rgba(99,102,241,0.15);
        background: var(--bg-glass-hover);
    }

    /* ── Animations ── */
    @keyframes slideInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulseRing {
        0%   { box-shadow: 0 0 0 0 rgba(16,185,129,0.6); }
        70%  { box-shadow: 0 0 0 10px rgba(16,185,129,0); }
        100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
    }

    @keyframes borderGlow {
        0%, 100% { border-color: var(--accent-primary); }
        50%      { border-color: var(--accent-secondary); }
    }
    
    @keyframes shimmer {
        0%   { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    @keyframes fadeInScale {
        0% { opacity: 0; transform: scale(0.95); }
        100% { opacity: 1; transform: scale(1); }
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: var(--bg-surface) !important;
        border-right: 1px solid var(--border-glass) !important;
        width: 240px !important;
        transition: width 0.3s ease;
    }
    
    .nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        margin: 8px 16px;
        border-radius: 8px;
        color: var(--text-secondary);
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        border-left: 3px solid transparent;
        text-decoration: none;
    }
    
    .nav-item:hover, .nav-item.active {
        background: var(--bg-glass-hover);
        color: var(--text-primary);
        border-left-color: var(--accent-primary);
    }
    
    .nav-item.active {
        animation: borderGlow 3s infinite;
        background: rgba(99,102,241,0.1);
        box-shadow: inset 20px 0 20px -20px rgba(99,102,241,0.2);
    }

    /* ── Tooltips ── */
    .header-tooltip-container {
        position: relative;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-left: 8px;
        cursor: pointer;
    }
    
    .header-tooltip-icon {
        color: var(--accent-secondary);
        font-size: 16px;
        opacity: 0.7;
        transition: opacity 0.2s, transform 0.2s;
    }
    
    .header-tooltip-container:hover .header-tooltip-icon {
        opacity: 1;
        transform: scale(1.1);
    }

    .header-tooltip-content {
        visibility: hidden;
        opacity: 0;
        position: absolute;
        top: 100%;
        left: 50%;
        transform: translateX(-50%) translateY(10px);
        background: rgba(10,10,15,0.95);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(99,102,241,0.3);
        border-radius: 12px;
        padding: 12px 16px;
        box-shadow: 0 0 30px rgba(99,102,241,0.2);
        max-width: 280px;
        width: max-content;
        z-index: 1000;
        text-align: left;
        pointer-events: none;
    }
    
    .header-tooltip-container:hover .header-tooltip-content {
        visibility: visible;
        opacity: 1;
        transform: translateX(-50%) translateY(5px);
        animation: fadeInScale 0.2s cubic-bezier(0.34,1.56,0.64,1);
    }

    /* ── Filter Bar ── */
    .filter-pill {
        background: var(--bg-glass);
        border: 1px solid var(--border-glass);
        color: var(--text-secondary);
        border-radius: 20px;
        padding: 6px 16px;
        font-size: 0.85rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .filter-pill:hover, .filter-pill.active {
        background: var(--accent-primary);
        color: white;
        border-color: var(--accent-primary);
        box-shadow: var(--glow-primary);
    }
    
    /* ── Buttons ── */
    .deploy-btn {
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: var(--glow-primary);
    }
    .deploy-btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 0 25px rgba(34,211,238,0.4);
    }
    
    /* Input Overrides */
    .stSelectbox div[data-baseweb="select"] > div {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-glass) !important;
        color: var(--text-primary) !important;
    }

    /* ── Toast Notification ── */
    .toast-notification {
        position: fixed;
        top: 20px;
        right: -400px;
        background: rgba(10,10,15,0.95);
        backdrop-filter: blur(20px);
        border-left: 4px solid var(--accent-danger);
        border-top: 1px solid var(--border-glass);
        border-bottom: 1px solid var(--border-glass);
        border-right: 1px solid var(--border-glass);
        padding: 16px 20px;
        border-radius: 8px;
        color: var(--text-primary);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        z-index: 9999;
        transition: right 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .toast-notification.show { right: 20px; }

    </style>
    """, unsafe_allow_html=True)
