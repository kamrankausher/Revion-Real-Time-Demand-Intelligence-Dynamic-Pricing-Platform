import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Cell,
} from 'recharts';
import { SkeletonChart } from '../common/Skeleton';
import { PromotionIcon } from '../common/Icons3D';

function GlassTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  if (!d) return null;
  return (
    <div className="glass-tooltip" style={{ minWidth: 150, fontSize: 11 }}>
      <div className="font-semibold mb-2" style={{ color: 'var(--text-primary)', fontSize: 12 }}>{d.category}</div>
      <div className="flex justify-between py-0.5">
        <span style={{ color: 'var(--text-secondary)' }}>Baseline</span>
        <span className="font-semibold mono-text" style={{ color: 'var(--text-primary)' }}>{d.baseline}</span>
      </div>
      <div className="flex justify-between py-0.5">
        <span style={{ color: 'var(--text-secondary)' }}>Promoted</span>
        <span className="font-semibold mono-text" style={{ color: 'var(--success)' }}>{d.promoted}</span>
      </div>
      <div className="flex justify-between pt-1 mt-1" style={{ borderTop: '1px solid var(--border)' }}>
        <span style={{ color: 'var(--text-secondary)' }}>Lift</span>
        <span className="font-bold mono-text" style={{ color: 'var(--success)' }}>+{d.lift}%</span>
      </div>
    </div>
  );
}

export default function PromotionImpact({ data, loading }) {
  if (loading) return <SkeletonChart height={260} />;

  const chartData = data.map((d) => ({ ...d, delta: d.promoted - d.baseline }));

  return (
    <div className="glass-card p-5 fade-in-up delay-4">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <PromotionIcon size={28} />
          <div>
            <h2 className="text-[15px] font-bold" style={{ color: 'var(--text-primary)' }}>Promotion Impact</h2>
            <p className="text-[11px] mt-0.5" style={{ color: 'var(--text-tertiary)' }}>Baseline vs promoted demand by department</p>
          </div>
        </div>
        <div className="flex items-center gap-4 text-[11px]" style={{ color: 'var(--text-secondary)' }}>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full" style={{ background: 'var(--text-tertiary)' }} /> Baseline
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full" style={{ background: 'var(--accent-purple)', boxShadow: '0 0 6px var(--accent-purple)' }} /> Promoted
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={chartData} barGap={3} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
          <defs>
            <linearGradient id="promoBarGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#A855F7" stopOpacity={0.9} />
              <stop offset="100%" stopColor="#22D3EE" stopOpacity={0.6} />
            </linearGradient>
          </defs>
          <CartesianGrid vertical={false} strokeDasharray="none" stroke="var(--border-subtle)" />
          <XAxis dataKey="category" tick={{ fontSize: 11, fill: 'var(--text-tertiary)' }}
            axisLine={{ stroke: 'var(--border)' }} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: 'var(--text-tertiary)' }}
            axisLine={false} tickLine={false} width={40} />
          <Tooltip content={<GlassTooltip />} cursor={{ fill: 'rgba(var(--accent-rgb),0.03)' }} />
          <Bar dataKey="baseline" radius={[4, 4, 0, 0]} fill="var(--text-tertiary)" fillOpacity={0.25} barSize={22} />
          <Bar dataKey="promoted" radius={[4, 4, 0, 0]} barSize={22}>
            {chartData.map((_, i) => (
              <Cell key={i} fill="url(#promoBarGrad)" />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Lift badges */}
      <div className="flex gap-2 mt-4">
        {data.map((d) => (
          <div
            key={d.category}
            className="flex-1 text-center py-2 rounded-lg text-xs"
            style={{
              background: 'linear-gradient(135deg, rgba(var(--accent-purple-rgb),0.08), rgba(var(--accent-rgb),0.05))',
              border: '1px solid rgba(var(--accent-purple-rgb),0.12)',
            }}
          >
            <span className="font-medium" style={{ color: 'var(--text-secondary)' }}>{d.category}</span>
            <span className="font-bold ml-1.5 mono-text" style={{ color: 'var(--accent-purple)' }}>+{d.lift}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
