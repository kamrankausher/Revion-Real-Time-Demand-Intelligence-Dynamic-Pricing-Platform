import streamlit as st
import streamlit.components.v1 as components

def inject_particle_network():
    """Injects a JS canvas particle network into the parent Streamlit DOM's hero-header."""
    js_code = """
    <script>
    (function() {
        const parentDoc = window.parent.document;
        // Wait for the hero header to exist
        const checkExist = setInterval(function() {
            const heroHeader = parentDoc.querySelector('.hero-header');
            if (heroHeader) {
                clearInterval(checkExist);
                if (!heroHeader.querySelector('canvas.particle-network')) {
                    const canvas = parentDoc.createElement('canvas');
                    canvas.className = 'particle-network';
                    canvas.style.position = 'absolute';
                    canvas.style.top = '0';
                    canvas.style.left = '0';
                    canvas.style.width = '100%';
                    canvas.style.height = '100%';
                    canvas.style.zIndex = '0';
                    canvas.style.pointerEvents = 'none';
                    canvas.style.opacity = '0.6';
                    
                    heroHeader.style.position = 'relative';
                    heroHeader.style.overflow = 'hidden';
                    heroHeader.style.borderRadius = '16px';
                    heroHeader.style.padding = '30px';
                    // We need to ensure text is above the canvas
                    Array.from(heroHeader.children).forEach(child => {
                        if (child.tagName !== 'CANVAS') {
                            child.style.position = 'relative';
                            child.style.zIndex = '1';
                        }
                    });
                    
                    heroHeader.insertBefore(canvas, heroHeader.firstChild);
                    
                    // Particle Animation Logic
                    const ctx = canvas.getContext('2d');
                    let particles = [];
                    let w, h;
                    
                    function resize() {
                        w = canvas.width = heroHeader.offsetWidth;
                        h = canvas.height = heroHeader.offsetHeight;
                    }
                    resize();
                    parentDoc.defaultView.addEventListener('resize', resize);
                    
                    class Particle {
                        constructor() {
                            this.x = Math.random() * w;
                            this.y = Math.random() * h;
                            this.vx = (Math.random() - 0.5) * 0.5;
                            this.vy = (Math.random() - 0.5) * 0.5;
                            this.radius = Math.random() * 1.5 + 0.5;
                        }
                        update() {
                            this.x += this.vx;
                            this.y += this.vy;
                            if (this.x < 0 || this.x > w) this.vx *= -1;
                            if (this.y < 0 || this.y > h) this.vy *= -1;
                        }
                        draw() {
                            ctx.beginPath();
                            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                            ctx.fillStyle = '#22d3ee';
                            ctx.fill();
                        }
                    }
                    
                    for (let i = 0; i < 40; i++) {
                        particles.push(new Particle());
                    }
                    
                    function animate() {
                        ctx.clearRect(0, 0, w, h);
                        for (let i = 0; i < particles.length; i++) {
                            particles[i].update();
                            particles[i].draw();
                            for (let j = i + 1; j < particles.length; j++) {
                                const dx = particles[i].x - particles[j].x;
                                const dy = particles[i].y - particles[j].y;
                                const dist = Math.sqrt(dx * dx + dy * dy);
                                if (dist < 80) {
                                    ctx.beginPath();
                                    ctx.moveTo(particles[i].x, particles[i].y);
                                    ctx.lineTo(particles[j].x, particles[j].y);
                                    ctx.strokeStyle = `rgba(34, 211, 238, ${1 - dist/80})`;
                                    ctx.lineWidth = 0.5;
                                    ctx.stroke();
                                }
                            }
                        }
                        requestAnimationFrame(animate);
                    }
                    animate();
                }
            }
        }, 100);
    })();
    </script>
    """
    components.html(js_code, height=0, width=0)

def activity_feed():
    st.markdown("""
    <div class="chart-container" style="margin-top: 1rem; max-height: 340px; overflow-y: auto;">
        <div class="section-header" style="margin-top: 0; padding-top: 0;">
            Live System Activity <span class="section-tag">REAL-TIME</span>
        </div>
        <div class="activity-feed">
            <div class="feed-item">
                <div class="feed-time">Just now</div>
                <div class="feed-content">
                    <span style="color: var(--accent-cyan);">[Pricing]</span> Optimized price for <b>FOODS_3_090</b> (+2.1% lift)
                </div>
            </div>
            <div class="feed-item">
                <div class="feed-time">2m ago</div>
                <div class="feed-content">
                    <span style="color: var(--accent-rose);">[Anomaly]</span> Spike detected in <b>TX_2</b> demand (Severity: High)
                </div>
            </div>
            <div class="feed-item">
                <div class="feed-time">15m ago</div>
                <div class="feed-content">
                    <span style="color: var(--accent-blue);">[Forecast]</span> Model retraining completed. WRMSSE improved by 0.02.
                </div>
            </div>
            <div class="feed-item">
                <div class="feed-time">42m ago</div>
                <div class="feed-content">
                    <span style="color: var(--accent-purple);">[Causal]</span> DiD analysis for 'Super Bowl Promo' finalized.
                </div>
            </div>
            <div class="feed-item">
                <div class="feed-time">1h ago</div>
                <div class="feed-content">
                    <span style="color: var(--accent-green);">[System]</span> Daily data ingestion successful (42,840 series updated).
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
