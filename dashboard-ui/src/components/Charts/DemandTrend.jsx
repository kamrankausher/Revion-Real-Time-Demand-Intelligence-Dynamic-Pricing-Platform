import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip,
} from 'recharts';
import { formatDate, formatDateFull } from '../../utils/formatters';
import { SkeletonChart } from '../common/Skeleton';
import { TrendIcon } from '../common/Icons3D';

function GlassTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-tooltip" style={{ minWidth: 150 }}>
      <div className="font-semibold mb-2" style={{ color: 'var(--text-primary)', fontSize: 12 }}>
        {formatDateFull(label)}
      </div>
      {payload.map((entry) => (
        <div key={entry.dataKey} className="flex justify-between gap-4 py-0.5" style={{ fontSize: 11 }}>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full" style={{ background: entry.color, boxShadow: `0 0 6px ${entry.color}` }} />
            <span style={{ color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{entry.dataKey}</span>
          </span>
          <span className="font-semibold mono-text" style={{ color: 'var(--text-primary)' }}>{entry.value}</span>
        </div>
      ))}
    </div>
  );
}

const LEGEND = [
  { key: 'foods', label: 'Foods', color: '#00E5FF' },
  { key: 'household', label: 'Household', color: '#A855F7' },
  { key: 'hobbies', label: 'Hobbies', color: '#F59E0B' },
];

export default function DemandTrend({ data, loading }) {
  if (loading) return <SkeletonChart height={200} />;

  return (
    <div className="glass-card p-5 fade-in-up delay-2">
      <div className="flex items-center gap-3 mb-5">
        <TrendIcon size={24} />
        <div>
          <h2 className="text-[15px] font-bold" style={{ color: 'var(--text-primary)' }}>
            Category Trends
          </h2>
          <p className="text-[11px] mt-0.5" style={{ color: 'var(--text-tertiary)' }}>
            30-day moving average by department
          </p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
          <CartesianGrid vertical={false} strokeDasharray="none" stroke="var(--border-subtle)" />
          <XAxis
            dataKey="date" tickFormatter={formatDate}
            tick={{ fontSize: 11, fill: 'var(--text-tertiary)' }}
            axisLine={{ stroke: 'var(--border)' }} tickLine={false} interval={6}
          />
          <YAxis
            tick={{ fontSize: 11, fill: 'var(--text-tertiary)' }}
            axisLine={false} tickLine={false} width={40}
          />
          <Tooltip content={<GlassTooltip />} />
          {LEGEND.map(l => (
            <Line key={l.key} dataKey={l.key} stroke={l.color} strokeWidth={2} dot={false}
              style={{ filter: `drop-shadow(0 0 4px ${l.color}66)` }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>

      <div className="flex items-center gap-5 mt-3">
        {LEGEND.map(l => (
          <span key={l.key} className="flex items-center gap-1.5 text-[11px] font-medium" style={{ color: 'var(--text-secondary)' }}>
            <span className="w-3 h-1 rounded-full" style={{ background: l.color, boxShadow: `0 0 6px ${l.color}66` }} />
            {l.label}
          </span>
        ))}
      </div>
    </div>
  );
}
