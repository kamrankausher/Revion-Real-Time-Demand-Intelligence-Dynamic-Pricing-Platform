import KPICard from './KPICard';
import { SkeletonCard } from '../common/Skeleton';

export default function KPIStrip({ data, loading }) {
  const keys = data ? Object.keys(data) : Array(5).fill(null);

  return (
    <div className="grid grid-cols-5 gap-4">
      {loading
        ? keys.map((_, i) => <SkeletonCard key={i} />)
        : keys.map((key, i) => (
            <KPICard key={key} data={data[key]} index={i} kpiKey={key} />
          ))}
    </div>
  );
}
