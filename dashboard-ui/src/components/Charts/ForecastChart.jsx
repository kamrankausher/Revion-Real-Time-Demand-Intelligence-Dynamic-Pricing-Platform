import {
  ResponsiveContainer, ComposedChart, Area, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ReferenceLine,
} from 'recharts';
import { formatDate, formatDateFull } from '../../utils/formatters';
import { SkeletonChart } from '../common/Skeleton';
import { ForecastIcon } from '../common/Icons3D';

function GlassTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-tooltip" style={{ minWidth: 170 }}>
      <div className="font-semibold mb-2" style={{ color: 'var(--text-primary)', fontSize: 12 }}>
        {formatDateFull(label)}
      </div>
      {payload.map((entry) => (
        <div key={entry.dataKey} className="flex justify-between gap-4 py-0.5" style={{ fontSize: 11 }}>
          <span className="flex items-center gap-1.5">
            <span
              className="w-2 h-2 rounded-full"
              style={{ background: entry.color, boxShadow: `0 0 6px ${entry.color}` }}
            />
            <span style={{ color: 'var(--text-secondary)' }}>
              {entry.dataKey === 'actual' ? 'Actual' :
               entry.dataKey === 'forecast' ? 'Forecast' :
               entry.dataKey === 'upper' ? 'Upper CI' : 'Lower CI'}
            </span>
          </span>
          <span className="font-semibold mono-text" style={{ color: 'var(--text-primary)' }}>
            {entry.value != null ? Math.round(entry.value) : '—'}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function ForecastChart({ data, loading }) {
  if (loading) return <SkeletonChart height={320} />;

  const splitIdx = data.findIndex((d) => d.forecast !== null);
  const splitDate = splitIdx > 0 ? data[splitIdx].date : null;

  return (
    <div className="glass-card p-5 fade-in-up">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <ForecastIcon size={28} />
          <div>
            <h2 className="text-[15px] font-bold" style={{ color: 'var(--text-primary)' }}>
              Demand Forecast
            </h2>
            <p className="text-[11px] mt-0.5" style={{ color: 'var(--text-tertiary)' }}>
              Historical actuals with 28-day forward projection
            </p>
          </div>
        </div>
        <div className="flex items-center gap-4 text-[11px]" style={{ color: 'var(--text-secondary)' }}>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full" style={{ background: 'var(--text-primary)', boxShadow: '0 0 4px var(--text-primary)' }} />
            Actual
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full" style={{ background: 'var(--accent)', boxShadow: '0 0 6px var(--accent)' }} />
            Forecast
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-5 h-2 rounded-sm" style={{ background: 'linear-gradient(90deg, var(--accent-purple), var(--accent))', opacity: 0.3 }} />
            95% CI
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={320}>
        <ComposedChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
          <defs>
            <linearGradient id="ciGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#A855F7" stopOpacity={0.15} />
              <stop offset="100%" stopColor="#00E5FF" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="none" vertical={false} stroke="var(--border-subtle)" />
          <XAxis
            dataKey="date" tickFormatter={formatDate}
            tick={{ fontSize: 11, fill: 'var(--text-tertiary)' }}
            axisLine={{ stroke: 'var(--border)' }} tickLine={false} interval={13}
          />
          <YAxis
            tick={{ fontSize: 11, fill: 'var(--text-tertiary)' }}
            axisLine={false} tickLine={false} width={40}
          />
          <Tooltip content={<GlassTooltip />} />
          <Area dataKey="upper" stroke="none" fill="url(#ciGradient)" connectNulls={false} />
          <Area dataKey="lower" stroke="none" fill="var(--bg-primary)" fillOpacity={0.8} connectNulls={false} />
          <Line dataKey="actual" stroke="var(--text-primary)" strokeWidth={1.5} dot={false} connectNulls={false} />
          <Line dataKey="forecast" stroke="var(--accent)" strokeWidth={2} strokeDasharray="6 3" dot={false} connectNulls={false}
            style={{ filter: 'drop-shadow(0 0 4px rgba(0,229,255,0.4))' }}
          />
          {splitDate && (
            <ReferenceLine x={splitDate} stroke="var(--accent-purple)" strokeDasharray="4 4" strokeOpacity={0.5}
              label={{ value: 'Today', position: 'insideTopRight', fill: 'var(--accent-purple)', fontSize: 10 }}
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
