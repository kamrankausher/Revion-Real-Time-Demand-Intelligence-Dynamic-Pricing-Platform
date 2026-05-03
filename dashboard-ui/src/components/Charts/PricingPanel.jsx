import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, ReferenceLine,
} from 'recharts';
import { SkeletonChart } from '../common/Skeleton';
import { PricingIcon, BoltIcon } from '../common/Icons3D';

function GlassTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  if (!d) return null;
  return (
    <div className="glass-tooltip">
      {[
        { label: 'Price', val: `$${d.price}`, color: 'var(--text-primary)' },
        { label: 'Demand', val: d.demand, color: 'var(--accent)' },
        { label: 'Revenue', val: `$${d.revenue}`, color: 'var(--accent-gold)' },
      ].map(r => (
        <div key={r.label} className="flex justify-between gap-4 py-0.5" style={{ fontSize: 11 }}>
          <span style={{ color: 'var(--text-secondary)' }}>{r.label}</span>
          <span className="font-semibold mono-text" style={{ color: r.color }}>{r.val}</span>
        </div>
      ))}
    </div>
  );
}

export default function PricingPanel({ data, loading }) {
  if (loading) return <SkeletonChart height={260} />;
  const { currentPrice, recommendedPrice, revenueCurve, expectedLift, confidence } = data;
  const priceDelta = ((recommendedPrice - currentPrice) / currentPrice * 100).toFixed(1);

  return (
    <div className="glass-card p-5 fade-in-up delay-3">
      <div className="flex items-center gap-3 mb-5">
        <PricingIcon size={28} />
        <div>
          <h2 className="text-[15px] font-bold" style={{ color: 'var(--text-primary)' }}>Dynamic Pricing</h2>
          <p className="text-[11px] mt-0.5" style={{ color: 'var(--text-tertiary)' }}>Revenue-optimal price recommendation</p>
        </div>
      </div>

      {/* Price comparison strip */}
      <div className="grid grid-cols-3 gap-3 mb-5">
        {/* Current */}
        <div className="rounded-xl p-3" style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)' }}>
          <div className="text-[10px] uppercase tracking-wider mb-1 font-semibold" style={{ color: 'var(--text-tertiary)' }}>Current</div>
          <div className="text-lg font-bold mono-text" style={{ color: 'var(--text-primary)' }}>${currentPrice}</div>
        </div>
        {/* Recommended */}
        <div className="rounded-xl p-3 pulse-glow" style={{
          background: 'linear-gradient(135deg, rgba(var(--accent-rgb),0.08), rgba(var(--accent-purple-rgb),0.05))',
          border: '1px solid rgba(var(--accent-rgb),0.2)',
        }}>
          <div className="text-[10px] uppercase tracking-wider mb-1 font-semibold" style={{ color: 'var(--accent)' }}>Recommended</div>
          <div className="text-lg font-bold mono-text" style={{ color: 'var(--accent)' }}>
            ${recommendedPrice}
            <span className="text-xs font-normal ml-1 opacity-70">({priceDelta}%)</span>
          </div>
        </div>
        {/* Expected Lift */}
        <div className="rounded-xl p-3" style={{
          background: 'linear-gradient(135deg, rgba(var(--success-rgb),0.08), transparent)',
          border: '1px solid rgba(var(--success-rgb),0.15)',
        }}>
          <div className="flex items-center gap-1 text-[10px] uppercase tracking-wider mb-1 font-semibold" style={{ color: 'var(--success)' }}>
            <BoltIcon size={12} /> Expected Lift
          </div>
          <div className="text-lg font-bold mono-text" style={{ color: 'var(--success)' }}>
            +{expectedLift}%
            <span className="text-xs font-normal ml-1 opacity-70">({(confidence * 100).toFixed(0)}% conf)</span>
          </div>
        </div>
      </div>

      {/* Revenue curve */}
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={revenueCurve} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
          <defs>
            <linearGradient id="revenueGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#F59E0B" stopOpacity={0.2} />
              <stop offset="100%" stopColor="#F59E0B" stopOpacity={0.01} />
            </linearGradient>
          </defs>
          <CartesianGrid vertical={false} strokeDasharray="none" stroke="var(--border-subtle)" />
          <XAxis dataKey="price" tick={{ fontSize: 11, fill: 'var(--text-tertiary)' }}
            axisLine={{ stroke: 'var(--border)' }} tickLine={false} tickFormatter={(v) => `$${v}`} />
          <YAxis tick={{ fontSize: 11, fill: 'var(--text-tertiary)' }}
            axisLine={false} tickLine={false} width={40} tickFormatter={(v) => `$${v}`} />
          <Tooltip content={<GlassTooltip />} />
          <Area dataKey="revenue" stroke="#F59E0B" strokeWidth={2} fill="url(#revenueGrad)"
            style={{ filter: 'drop-shadow(0 0 4px rgba(245,158,11,0.4))' }} />
          <ReferenceLine x={currentPrice} stroke="var(--text-tertiary)" strokeDasharray="4 4"
            label={{ value: 'Current', position: 'insideTopRight', fill: 'var(--text-tertiary)', fontSize: 10 }} />
          <ReferenceLine x={recommendedPrice} stroke="var(--accent)" strokeDasharray="4 4"
            label={{ value: 'Optimal', position: 'insideTopLeft', fill: 'var(--accent)', fontSize: 10 }} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
