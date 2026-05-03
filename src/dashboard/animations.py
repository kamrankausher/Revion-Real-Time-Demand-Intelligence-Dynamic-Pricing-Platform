import streamlit as st

def render_svg(svg_string):
    """Renders a responsive SVG inside a container."""
    st.markdown(
        f'<div class="animated-icon-container" style="width: 100%; max-width: 150px; margin: 0 auto;">{svg_string}</div>', 
        unsafe_allow_html=True
    )

# 1. Overview (Aura/Core) - Intersecting rotating rings
SVG_OVERVIEW = """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#22d3ee;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:0.2" />
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <style>
    .ring1 { transform-origin: center; animation: spin1 8s linear infinite; }
    .ring2 { transform-origin: center; animation: spin2 12s linear infinite; }
    .core { transform-origin: center; animation: pulse 3s ease-in-out infinite; }
    @keyframes spin1 { 100% { transform: rotate3d(1, 1, 0, 360deg); } }
    @keyframes spin2 { 100% { transform: rotate3d(0, 1, 1, -360deg); } }
    @keyframes pulse { 0%, 100% { transform: scale(1); opacity: 0.8; } 50% { transform: scale(1.1); opacity: 1; } }
  </style>
  <circle class="core" cx="50" cy="50" r="15" fill="url(#grad1)" filter="url(#glow)"/>
  <circle class="ring1" cx="50" cy="50" r="30" fill="none" stroke="#22d3ee" stroke-width="2" stroke-dasharray="20 10" filter="url(#glow)"/>
  <circle class="ring2" cx="50" cy="50" r="40" fill="none" stroke="#a78bfa" stroke-width="1.5" stroke-dasharray="40 20" filter="url(#glow)"/>
</svg>
"""

# 2. Forecast (Wave) - Animated glowing sine wave
SVG_FORECAST = """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#a78bfa;stop-opacity:0.2" />
      <stop offset="50%" style="stop-color:#22d3ee;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:0.2" />
    </linearGradient>
    <filter id="glow2">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <style>
    .wave { stroke-dasharray: 200; stroke-dashoffset: 200; animation: dash 3s linear infinite; }
    .grid { animation: pan 10s linear infinite; }
    @keyframes dash { to { stroke-dashoffset: 0; } }
    @keyframes pan { 100% { transform: translateX(-20px); } }
  </style>
  <g class="grid" stroke="rgba(255,255,255,0.05)" stroke-width="1">
    <line x1="0" y1="20" x2="120" y2="20" />
    <line x1="0" y1="50" x2="120" y2="50" />
    <line x1="0" y1="80" x2="120" y2="80" />
    <line x1="20" y1="0" x2="20" y2="100" />
    <line x1="50" y1="0" x2="50" y2="100" />
    <line x1="80" y1="0" x2="80" y2="100" />
    <line x1="110" y1="0" x2="110" y2="100" />
  </g>
  <path class="wave" d="M0,70 Q25,20 50,50 T100,30" fill="none" stroke="url(#grad2)" stroke-width="4" filter="url(#glow2)"/>
  <circle cx="100" cy="30" r="4" fill="#22d3ee" filter="url(#glow2)">
    <animate attributeName="opacity" values="0;1;0" dur="1.5s" repeatCount="indefinite" />
  </circle>
</svg>
"""

# 3. Dynamic Pricing (Diamond) - Rotating 3D crystal
SVG_PRICING = """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad3" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#34d399;stop-opacity:0.9" />
      <stop offset="100%" style="stop-color:#06b6d4;stop-opacity:0.3" />
    </linearGradient>
    <filter id="glow3">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <style>
    .diamond { transform-origin: 50px 50px; animation: floatSpin 6s ease-in-out infinite; }
    @keyframes floatSpin {
      0% { transform: translateY(0) rotateY(0deg); }
      50% { transform: translateY(-10px) rotateY(180deg); }
      100% { transform: translateY(0) rotateY(360deg); }
    }
  </style>
  <g class="diamond" filter="url(#glow3)">
    <polygon points="50,10 80,40 50,90 20,40" fill="url(#grad3)" stroke="#34d399" stroke-width="1.5"/>
    <polygon points="50,10 50,90 20,40" fill="rgba(255,255,255,0.1)" />
    <polygon points="50,10 80,40 50,40" fill="rgba(255,255,255,0.3)" />
  </g>
</svg>
"""

# 4. Anomaly Detection (Radar) - Expanding concentric ripples
SVG_ANOMALY = """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="glow4">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <style>
    .ripple1 { transform-origin: 50px 50px; animation: ripple 2s linear infinite; }
    .ripple2 { transform-origin: 50px 50px; animation: ripple 2s linear infinite 0.6s; }
    .ripple3 { transform-origin: 50px 50px; animation: ripple 2s linear infinite 1.2s; }
    .dot { transform-origin: 50px 50px; animation: blink 2s ease-in-out infinite; }
    @keyframes ripple {
      0% { transform: scale(0.2); opacity: 1; }
      100% { transform: scale(2.5); opacity: 0; }
    }
    @keyframes blink { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }
  </style>
  <circle class="ripple1" cx="50" cy="50" r="15" fill="none" stroke="#fb7185" stroke-width="2" filter="url(#glow4)"/>
  <circle class="ripple2" cx="50" cy="50" r="15" fill="none" stroke="#fb7185" stroke-width="2" filter="url(#glow4)"/>
  <circle class="ripple3" cx="50" cy="50" r="15" fill="none" stroke="#fb7185" stroke-width="2" filter="url(#glow4)"/>
  
  <circle class="dot" cx="70" cy="30" r="3" fill="#fbbf24" filter="url(#glow4)"/>
  <circle class="dot" cx="30" cy="60" r="4" fill="#fb7185" filter="url(#glow4)" style="animation-delay: 1s;"/>
  <circle cx="50" cy="50" r="4" fill="#f43f5e" filter="url(#glow4)"/>
</svg>
"""

# 5. Causal Analysis (Nodes) - Pulsing network graph
SVG_CAUSAL = """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="glow5">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <style>
    .node { animation: pulseNode 3s infinite alternate; }
    .edge { stroke-dasharray: 50; animation: flow 2s linear infinite; }
    @keyframes pulseNode {
      0% { r: 4; fill: #22d3ee; }
      100% { r: 6; fill: #a78bfa; }
    }
    @keyframes flow {
      0% { stroke-dashoffset: 50; }
      100% { stroke-dashoffset: 0; }
    }
  </style>
  <line class="edge" x1="20" y1="50" x2="50" y2="20" stroke="rgba(34,211,238,0.5)" stroke-width="2" />
  <line class="edge" x1="20" y1="50" x2="50" y2="80" stroke="rgba(34,211,238,0.5)" stroke-width="2" style="animation-direction: reverse;"/>
  <line class="edge" x1="50" y1="20" x2="80" y2="50" stroke="rgba(167,139,250,0.5)" stroke-width="2" />
  <line class="edge" x1="50" y1="80" x2="80" y2="50" stroke="rgba(167,139,250,0.5)" stroke-width="2" />
  <line class="edge" x1="50" y1="20" x2="50" y2="80" stroke="rgba(255,255,255,0.1)" stroke-width="1" />
  
  <circle class="node" cx="20" cy="50" r="5" fill="#22d3ee" filter="url(#glow5)" style="animation-delay: 0s;" />
  <circle class="node" cx="50" cy="20" r="5" fill="#22d3ee" filter="url(#glow5)" style="animation-delay: 0.5s;" />
  <circle class="node" cx="50" cy="80" r="5" fill="#22d3ee" filter="url(#glow5)" style="animation-delay: 1s;" />
  <circle class="node" cx="80" cy="50" r="5" fill="#22d3ee" filter="url(#glow5)" style="animation-delay: 1.5s;" />
</svg>
"""
