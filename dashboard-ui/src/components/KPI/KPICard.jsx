import { useEffect, useRef, useState } from 'react';
import { formatCurrency, formatNumber } from '../../utils/formatters';
import { getKPIIcon } from '../common/Icons3D';

function TrendIndicator({ value, isAnomaly }) {
  if (value === 0) return null;
  const isPositive = isAnomaly ? value < 0 : value > 0;
  const arrow = value > 0 ? '▲' : '▼';

  return (
    <span
      className="pill"
      style={{
        background: isPositive ? 'var(--success-light)' : 'var(--danger-light)',
        color: isPositive ? 'var(--success)' : 'var(--danger)',
        fontSize: 10,
        fontWeight: 700,
        padding: '2px 8px',
      }}
    >
      {arrow} {Math.abs(value).toFixed(1)}%
    </span>
  );
}

function AnimatedValue({ value, prefix = '', suffix = '' }) {
  const [display, setDisplay] = useState(0);
  const ref = useRef(null);

  useEffect(() => {
    const start = 0;
    const end = typeof value === 'number' ? value : parseFloat(value) || 0;
    const duration = 1200;
    const startTime = performance.now();

    function tick(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(start + (end - start) * eased);
      if (progress < 1) ref.current = requestAnimationFrame(tick);
    }
    ref.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(ref.current);
  }, [value]);

  let formatted;
  if (prefix === '$') {
    formatted = formatCurrency(Math.round(display), true);
  } else if (suffix === '%') {
    formatted = `${formatNumber(display, 1)}%`;
  } else {
    formatted = formatNumber(Math.round(display));
  }

  return <span className="mono-text">{formatted}</span>;
}

export default function KPICard({ data, index = 0, kpiKey }) {
  const { value, change, label, prefix, suffix, isAnomaly } = data;
  const IconComponent = getKPIIcon(kpiKey);

  return (
    <div
      className="glass-card p-5 cursor-default fade-in-up"
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <IconComponent size={24} />
          <span
            className="text-[11px] font-semibold uppercase tracking-wider"
            style={{ color: 'var(--text-tertiary)' }}
          >
            {label}
          </span>
        </div>
        <TrendIndicator value={change} isAnomaly={isAnomaly} />
      </div>
      <div
        className="text-2xl font-bold tracking-tight"
        style={{ color: isAnomaly && value > 0 ? 'var(--danger)' : 'var(--text-primary)' }}
      >
        <AnimatedValue value={value} prefix={prefix} suffix={suffix} />
      </div>
    </div>
  );
}
