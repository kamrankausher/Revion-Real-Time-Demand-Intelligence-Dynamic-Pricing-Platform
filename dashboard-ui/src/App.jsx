import { useEffect, useState } from 'react';
import useStore from './store/useStore';
import Navbar from './components/Layout/Navbar';
import KPIStrip from './components/KPI/KPIStrip';
import ForecastChart from './components/Charts/ForecastChart';
import PromotionImpact from './components/Charts/PromotionImpact';
import PricingPanel from './components/Charts/PricingPanel';
import AnomalyTimeline from './components/Charts/AnomalyTimeline';
import DemandTrend from './components/Charts/DemandTrend';
import {
  generateKPIData,
  generateForecastData,
  generatePromotionData,
  generatePricingData,
  generateAnomalyData,
  generateDemandTrend,
} from './data/mockData';

function useDashboardData() {
  const { setLoading } = useStore();
  const [data, setData] = useState({
    kpi: null,
    forecast: null,
    promotion: null,
    pricing: null,
    anomaly: null,
    trend: null,
  });

  useEffect(() => {
    // Simulate staggered API loading — feels natural
    const timers = [];

    timers.push(setTimeout(() => {
      setData((prev) => ({ ...prev, kpi: generateKPIData() }));
      setLoading('kpi', false);
    }, 400));

    timers.push(setTimeout(() => {
      setData((prev) => ({ ...prev, trend: generateDemandTrend() }));
    }, 600));

    timers.push(setTimeout(() => {
      setData((prev) => ({ ...prev, forecast: generateForecastData() }));
      setLoading('forecast', false);
    }, 800));

    timers.push(setTimeout(() => {
      setData((prev) => ({ ...prev, promotion: generatePromotionData() }));
      setLoading('promotion', false);
    }, 1000));

    timers.push(setTimeout(() => {
      setData((prev) => ({ ...prev, pricing: generatePricingData() }));
      setLoading('pricing', false);
    }, 1100));

    timers.push(setTimeout(() => {
      setData((prev) => ({ ...prev, anomaly: generateAnomalyData() }));
      setLoading('anomaly', false);
    }, 1300));

    return () => timers.forEach(clearTimeout);
  }, [setLoading]);

  return data;
}

function SectionLabel({ children }) {
  return (
    <div className="flex items-center gap-3 mt-10 mb-4">
      <h2
        className="text-xs font-semibold uppercase tracking-widest"
        style={{ color: 'var(--text-tertiary)' }}
      >
        {children}
      </h2>
      <div className="flex-1 h-px" style={{ background: 'var(--border)' }} />
    </div>
  );
}

export default function App() {
  const { theme, loading } = useStore();
  const data = useDashboardData();

  // Initialize theme on mount
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-primary)' }}>
      <Navbar />

      {/* Main Content */}
      <main className="max-w-[1400px] mx-auto px-6 pb-12" style={{ paddingTop: '80px' }}>
        {/* KPI Strip */}
        <KPIStrip data={data.kpi} loading={loading.kpi} />

        {/* Hero: Forecast */}
        <SectionLabel>Forecasting</SectionLabel>
        <div className="grid grid-cols-3 gap-4">
          <div className="col-span-2">
            <ForecastChart data={data.forecast} loading={loading.forecast} />
          </div>
          <div>
            <DemandTrend data={data.trend} loading={loading.forecast} />
          </div>
        </div>

        {/* Row 2: Pricing + Promotion */}
        <SectionLabel>Pricing & Promotions</SectionLabel>
        <div className="grid grid-cols-2 gap-4">
          <PricingPanel data={data.pricing} loading={loading.pricing} />
          <PromotionImpact data={data.promotion} loading={loading.promotion} />
        </div>

        {/* Row 3: Anomalies */}
        <SectionLabel>Anomaly Detection</SectionLabel>
        <AnomalyTimeline data={data.anomaly} loading={loading.anomaly} />

        {/* Footer */}
        <div className="mt-12 pt-6 flex items-center justify-between text-[11px]" style={{ borderTop: '1px solid var(--border)', color: 'var(--text-tertiary)' }}>
          <span>Nexus Pricing Intelligence — Internal Tool</span>
          <span>Last synced: {new Date().toLocaleString()}</span>
        </div>
      </main>
    </div>
  );
}
