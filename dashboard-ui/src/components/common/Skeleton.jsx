export default function Skeleton({ width = '100%', height = 20, rounded = false, className = '' }) {
  return (
    <div
      className={`skeleton ${className}`}
      style={{
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height,
        borderRadius: rounded ? '50%' : 'var(--radius-sm)',
      }}
    />
  );
}

export function SkeletonCard() {
  return (
    <div className="glass-card p-5">
      <div className="flex items-center gap-2 mb-3">
        <Skeleton width={24} height={24} rounded />
        <Skeleton width={80} height={10} />
      </div>
      <Skeleton width={120} height={28} className="mb-2" />
      <Skeleton width={60} height={14} />
    </div>
  );
}

export function SkeletonChart({ height = 280 }) {
  return (
    <div className="glass-card p-5">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-2">
          <Skeleton width={28} height={28} rounded />
          <Skeleton width={140} height={16} />
        </div>
        <Skeleton width={80} height={12} />
      </div>
      <Skeleton width="100%" height={height} />
    </div>
  );
}
