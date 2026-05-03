import { useState } from 'react';
import {
  ResponsiveContainer, ComposedChart, Area, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, Scatter,
} from 'recharts';
import { formatDate, formatDateFull } from '../../utils/formatters';
import { SkeletonChart } from '../common/Skeleton';
import { AnomalyIcon } from '../common/Icons3D';

function GlassTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  if (!d) return null;
  return (
    <div className="glass-tooltip" style={{ minWidth: 180, fontSize: 11 }}>
      <div className="font-semibold mb-2" style={{ color: 'var(--text-primary)', fontSize: 12 }}>{formatDateFull(d.date)}</div>
      <div className="flex justify-between gap-4 py-0.5">
        <span style={{ color: 'var(--text-secondary)' }}>Value</span>
        <span className="font-semibold mono-text" style={{ color: 'var(--text-primary)' }}>{d.value}</span>
      </div>
      {d.isAnomaly && (
        <>
          <div className="flex justify-between gap-4 py-0.5">
            <span style={{ color: 'var(--text-secondary)' }}>Score</span>
            <span className="font-semibold mono-text" style={{ color: 'var(--danger)' }}>{d.score}σ</span>
          </div>
          <div className="mt-1.5 pt-1.5" style={{ borderTop: '1px solid var(--border)' }}>
            <span style={{ color: 'var(--danger)' }}>{d.reason}</span>
          </div>
        </>
      )}
    </div>
  );
}

function AnomalyDetail({ anomaly, onClose }) {
  if (!anomaly) return null;
  const shapValues = [
    { feature: 'Price Change', contribution: 0.42 },
    { feature: 'Day of Week', contribution: 0.28 },
    { feature: 'Snap Event', contribution: 0.18 },
    { feature: 'Rolling Mean', contribution: 0.08 },
    { feature: 'Lag-7', contribution: 0.04 },
  ];

  return (
    <div className="glass-card p-5 mt-4 fade-in-up">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold" style={{ color: 'var(--danger)' }}>
            Root Cause Analysis
          </h3>
          <p className="text-[11px] mt-0.5" style={{ color: 'var(--text-tertiary)' }}>
            SHAP feature contributions — {formatDateFull(anomaly.date)}
          </p>
        </div>
        <button
          onClick={onClose}
          className="w-7 h-7 rounded-lg flex items-center justify-center text-xs"
          style={{
            color: 'var(--text-tertiary)',
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border)',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--danger)'; e.currentTarget.style.color = 'var(--danger)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text-tertiary)'; }}
        >
          ✕
        </button>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {shapValues.map((s, i) => (
          <div key={s.feature} className="flex items-center gap-3 fade-in-up" style={{ animationDelay: `${i * 0.08}s` }}>
            <span className="text-xs w-24 shrink-0 font-medium" style={{ color: 'var(--text-secondary)' }}>{s.feature}</span>
            <div className="progress-bar-track flex-1">
              <div
                className="progress-bar-fill"
                style={{
                  width: `${s.contribution * 100}%`,
                  background: s.contribution > 0.3
                    ? 'linear-gradient(90deg, var(--danger), #FB923C)'
                    : 'linear-gradient(90deg, var(--accent), var(--accent-purple))',
                  transitionDelay: `${i * 0.1}s`,
                }}
              />
            </div>
            <span className="text-xs font-bold mono-text w-10 text-right" style={{ color: 'var(--text-primary)' }}>
              {(s.contribution * 100).toFixed(0)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function AnomalyTimeline({ data, loading }) {
  const [selected, setSelected] = useState(null);
  if (loading) return <SkeletonChart height={280} />;

  const anomalies = data.filter((d) => d.isAnomaly);
  const anomalyData = data.map((d) => ({ ...d, anomalyValue: d.isAnomaly ? d.value : null }));

  return (
    <div className="fade-in-up delay-5">
      <div className="glass-card p-5">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <AnomalyIcon size={28} />
            <div>
              <h2 className="text-[15px] font-bold" style={{ color: 'var(--text-primary)' }}>Anomaly Detection</h2>
              <p className="text-[11px] mt-0.5" style={{ color: 'var(--text-tertiary)' }}>
                STL + Isolation Forest — click anomaly for root cause
              </p>
            </div>
          </div>
          <div className="pill pill-danger" style={{ fontSize: 11 }}>
            <span className="live-dot" style={{ background: 'var(--danger)', width: 5, height: 5 }} />
            {anomalies.length} detected
          </div>
        </div>

        <ResponsiveContainer width="100%" height={280}>
          <ComposedChart data={anomalyData} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
            <defs>
              <linearGradient id="anomAreaGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#A855F7" stopOpacity={0.06} />
                <stop offset="100%" stopColor="#00E5FF" stopOpacity={0.01} />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} strokeDasharray="none" stroke="var(--border-subtle)" />
            <XAxis dataKey="date" tickFormatter={formatDate}
              tick={{ fontSize: 11, fill: 'var(--text-tertiary)' }}
              axisLine={{ stroke: 'var(--border)' }} tickLine={false} interval={29} />
            <YAxis tick={{ fontSize: 11, fill: 'var(--text-tertiary)' }}
              axisLine={false} tickLine={false} width={40} />
            <Tooltip content={<GlassTooltip />} />
            <Area dataKey="value" stroke="none" fill="url(#anomAreaGrad)" />
            <Line dataKey="value" stroke="var(--text-secondary)" strokeWidth={1.5} dot={false}
              style={{ filter: 'drop-shadow(0 0 2px rgba(168,85,247,0.3))' }} />
            <Scatter dataKey="anomalyValue" fill="var(--danger)" r={6}
              cursor="pointer"
              onClick={(e) => { if (e?.payload?.isAnomaly) setSelected(e.payload); }}
              style={{ filter: 'drop-shadow(0 0 6px rgba(244,63,94,0.6))' }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <AnomalyDetail anomaly={selected} onClose={() => setSelected(null)} />
    </div>
  );
}
