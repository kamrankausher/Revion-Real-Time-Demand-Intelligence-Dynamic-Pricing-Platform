/* 3D SVG Icon Library — Premium gradient icons with depth */

export function RevenueIcon({ size = 28 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" className="icon-3d">
      <defs>
        <linearGradient id="rev-grad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#22D3EE" />
          <stop offset="100%" stopColor="#A855F7" />
        </linearGradient>
        <filter id="rev-shadow"><feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="#22D3EE" floodOpacity="0.3"/></filter>
      </defs>
      <rect x="3" y="3" width="26" height="26" rx="7" fill="url(#rev-grad)" filter="url(#rev-shadow)" opacity="0.15"/>
      <text x="16" y="21" textAnchor="middle" fill="url(#rev-grad)" fontSize="16" fontWeight="700" fontFamily="Outfit">$</text>
    </svg>
  );
}

export function AccuracyIcon({ size = 28 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" className="icon-3d">
      <defs>
        <linearGradient id="acc-grad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#00E5FF" />
          <stop offset="100%" stopColor="#06B6D4" />
        </linearGradient>
        <filter id="acc-shadow"><feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="#00E5FF" floodOpacity="0.3"/></filter>
      </defs>
      <circle cx="16" cy="16" r="12" fill="none" stroke="url(#acc-grad)" strokeWidth="2" filter="url(#acc-shadow)" opacity="0.3"/>
      <circle cx="16" cy="16" r="7" fill="none" stroke="url(#acc-grad)" strokeWidth="2" opacity="0.5"/>
      <circle cx="16" cy="16" r="3" fill="url(#acc-grad)"/>
    </svg>
  );
}

export function PromotionIcon({ size = 28 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" className="icon-3d">
      <defs>
        <linearGradient id="promo-grad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#A855F7" />
          <stop offset="100%" stopColor="#EC4899" />
        </linearGradient>
        <filter id="promo-shadow"><feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="#A855F7" floodOpacity="0.3"/></filter>
      </defs>
      <path d="M16 4L20 12L28 13.5L22 19.5L23.5 28L16 24L8.5 28L10 19.5L4 13.5L12 12Z" fill="url(#promo-grad)" filter="url(#promo-shadow)" opacity="0.85"/>
    </svg>
  );
}

export function AnomalyIcon({ size = 28 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" className="icon-3d">
      <defs>
        <linearGradient id="anom-grad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#F43F5E" />
          <stop offset="100%" stopColor="#FB923C" />
        </linearGradient>
        <filter id="anom-shadow"><feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="#F43F5E" floodOpacity="0.3"/></filter>
      </defs>
      <path d="M16 3L29 27H3L16 3Z" fill="none" stroke="url(#anom-grad)" strokeWidth="2" filter="url(#anom-shadow)"/>
      <text x="16" y="23" textAnchor="middle" fill="url(#anom-grad)" fontSize="14" fontWeight="700" fontFamily="Outfit">!</text>
    </svg>
  );
}

export function PricingIcon({ size = 28 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" className="icon-3d">
      <defs>
        <linearGradient id="price-grad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#F59E0B" />
          <stop offset="100%" stopColor="#FBBF24" />
        </linearGradient>
        <filter id="price-shadow"><feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="#F59E0B" floodOpacity="0.3"/></filter>
      </defs>
      <rect x="4" y="8" width="24" height="16" rx="4" fill="none" stroke="url(#price-grad)" strokeWidth="2" filter="url(#price-shadow)"/>
      <line x1="4" y1="14" x2="28" y2="14" stroke="url(#price-grad)" strokeWidth="1.5" opacity="0.5"/>
      <circle cx="22" cy="20" r="2" fill="url(#price-grad)"/>
    </svg>
  );
}

export function ForecastIcon({ size = 28 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" className="icon-3d">
      <defs>
        <linearGradient id="fc-grad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#00E5FF" />
          <stop offset="100%" stopColor="#A855F7" />
        </linearGradient>
        <filter id="fc-shadow"><feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="#00E5FF" floodOpacity="0.3"/></filter>
      </defs>
      <polyline points="4,24 10,18 16,20 22,10 28,6" fill="none" stroke="url(#fc-grad)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" filter="url(#fc-shadow)"/>
      <circle cx="28" cy="6" r="2.5" fill="url(#fc-grad)"/>
      <line x1="22" y1="10" x2="28" y2="6" stroke="url(#fc-grad)" strokeWidth="1" strokeDasharray="2 2" opacity="0.5"/>
    </svg>
  );
}

export function TrendIcon({ size = 28 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" className="icon-3d">
      <defs>
        <linearGradient id="trend-grad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#22D3EE" />
          <stop offset="50%" stopColor="#A855F7" />
          <stop offset="100%" stopColor="#F59E0B" />
        </linearGradient>
      </defs>
      <path d="M4 26 Q10 14, 16 18 Q22 22, 28 8" fill="none" stroke="url(#trend-grad)" strokeWidth="2.5" strokeLinecap="round"/>
      <path d="M4 26 Q10 14, 16 18 Q22 22, 28 8 L28 26 Z" fill="url(#trend-grad)" opacity="0.08"/>
    </svg>
  );
}

export function BoltIcon({ size = 20 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className="icon-3d">
      <defs>
        <linearGradient id="bolt-grad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#F59E0B" />
          <stop offset="100%" stopColor="#FBBF24" />
        </linearGradient>
      </defs>
      <path d="M13 2L4 14h6l-1 8 9-12h-6l1-8z" fill="url(#bolt-grad)"/>
    </svg>
  );
}

export function SunIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="5"/>
      <line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
      <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
    </svg>
  );
}

export function MoonIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    </svg>
  );
}

export function FilterIcon({ size = 16 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" strokeWidth="2" strokeLinecap="round">
      <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
    </svg>
  );
}

export function ClockIcon({ size = 14 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" strokeWidth="2" strokeLinecap="round">
      <circle cx="12" cy="12" r="10"/>
      <polyline points="12 6 12 12 16 14"/>
    </svg>
  );
}

export function LogoIcon({ size = 28 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" className="icon-3d">
      <defs>
        <linearGradient id="logo-grad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#00E5FF" />
          <stop offset="50%" stopColor="#A855F7" />
          <stop offset="100%" stopColor="#F59E0B" />
        </linearGradient>
        <filter id="logo-glow">
          <feDropShadow dx="0" dy="0" stdDeviation="3" floodColor="#00E5FF" floodOpacity="0.5"/>
        </filter>
      </defs>
      <rect x="2" y="2" width="28" height="28" rx="8" fill="url(#logo-grad)" filter="url(#logo-glow)" opacity="0.9"/>
      <text x="16" y="21" textAnchor="middle" fill="white" fontSize="12" fontWeight="800" fontFamily="Outfit">DI</text>
    </svg>
  );
}

/* Map KPI keys to icons */
const KPI_ICON_MAP = {
  totalRevenue: RevenueIcon,
  forecastAccuracy: AccuracyIcon,
  promotionLift: PromotionIcon,
  anomalyCount: AnomalyIcon,
  avgPriceChange: PricingIcon,
};

export function getKPIIcon(key) {
  return KPI_ICON_MAP[key] || BoltIcon;
}
