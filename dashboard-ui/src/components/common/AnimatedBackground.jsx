import { useEffect, useRef } from 'react';

class Particle {
  constructor(canvas) {
    this.canvas = canvas;
    this.reset();
  }
  reset() {
    this.x = Math.random() * this.canvas.width;
    this.y = Math.random() * this.canvas.height;
    this.vx = (Math.random() - 0.5) * 0.3;
    this.vy = (Math.random() - 0.5) * 0.3;
    this.radius = Math.random() * 1.5 + 0.5;
    this.opacity = Math.random() * 0.4 + 0.1;
    this.hue = Math.random() > 0.5 ? 185 : 270;
  }
  update() {
    this.x += this.vx;
    this.y += this.vy;
    if (this.x < 0 || this.x > this.canvas.width) this.vx *= -1;
    if (this.y < 0 || this.y > this.canvas.height) this.vy *= -1;
  }
  draw(ctx) {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = `hsla(${this.hue}, 80%, 65%, ${this.opacity})`;
    ctx.fill();
  }
}

export default function AnimatedBackground() {
  const canvasRef = useRef(null);
  const animRef = useRef(null);
  const particlesRef = useRef([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const resize = () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight; };
    resize();
    window.addEventListener('resize', resize);
    particlesRef.current = Array.from({ length: 55 }, () => new Particle(canvas));

    function animate() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const pts = particlesRef.current;
      pts.forEach(p => { p.update(); p.draw(ctx); });
      for (let i = 0; i < pts.length; i++) {
        for (let j = i + 1; j < pts.length; j++) {
          const dx = pts[i].x - pts[j].x, dy = pts[i].y - pts[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 140) {
            ctx.beginPath();
            ctx.moveTo(pts[i].x, pts[i].y);
            ctx.lineTo(pts[j].x, pts[j].y);
            ctx.strokeStyle = `rgba(0,229,255,${(1 - dist / 140) * 0.12})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }
      animRef.current = requestAnimationFrame(animate);
    }
    animate();
    return () => { window.removeEventListener('resize', resize); cancelAnimationFrame(animRef.current); };
  }, []);

  return (
    <>
      <canvas ref={canvasRef} className="animated-bg-canvas" />
      <div className="bg-gradient-overlay" />
    </>
  );
}
