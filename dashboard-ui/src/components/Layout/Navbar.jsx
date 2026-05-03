import useStore from '../../store/useStore';
import { STORES, CATEGORIES } from '../../data/mockData';
import { LogoIcon, SunIcon, MoonIcon, FilterIcon } from '../common/Icons3D';

const DATE_RANGES = [
  { label: '7D', value: '7d' },
  { label: '30D', value: '30d' },
  { label: '90D', value: '90d' },
  { label: 'YTD', value: 'ytd' },
];

export default function Navbar() {
  const { theme, toggleTheme, selectedStore, setStore, selectedCategory, setCategory, dateRange, setDateRange } = useStore();

  return (
    <header
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6"
      style={{
        height: 60,
        background: 'var(--bg-surface)',
        backdropFilter: 'var(--glass-blur)',
        WebkitBackdropFilter: 'var(--glass-blur)',
        borderBottom: '1px solid var(--border)',
        boxShadow: '0 4px 30px rgba(0,0,0,0.2)',
      }}
    >
      {/* Left — Brand */}
      <div className="flex items-center gap-3">
        <div className="float-anim">
          <LogoIcon size={32} />
        </div>
        <div>
          <span className="text-sm font-bold gradient-text">
            Nexus Pricing Intelligence
          </span>
        </div>
        <div className="pill pill-accent" style={{ fontSize: 10, padding: '2px 10px' }}>
          <span className="live-dot" />
          LIVE
        </div>
      </div>

      {/* Right — Controls */}
      <div className="flex items-center gap-3">
        {/* Date Range Pills */}
        <div
          className="flex rounded-xl p-1"
          style={{
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border)',
          }}
        >
          {DATE_RANGES.map((r) => (
            <button
              key={r.value}
              onClick={() => setDateRange(r.value)}
              className="px-3 py-1 text-xs font-semibold rounded-lg"
              style={{
                background: dateRange === r.value
                  ? 'linear-gradient(135deg, rgba(var(--accent-rgb),0.15), rgba(var(--accent-purple-rgb),0.1))'
                  : 'transparent',
                color: dateRange === r.value ? 'var(--accent)' : 'var(--text-tertiary)',
                border: dateRange === r.value ? '1px solid rgba(var(--accent-rgb),0.2)' : '1px solid transparent',
                transition: 'all 0.25s ease',
                cursor: 'pointer',
              }}
            >
              {r.label}
            </button>
          ))}
        </div>

        {/* Store Filter */}
        <div className="flex items-center gap-1.5">
          <FilterIcon size={14} />
          <select
            value={selectedStore}
            onChange={(e) => setStore(e.target.value)}
            className="glass-select"
          >
            {STORES.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        {/* Category Filter */}
        <select
          value={selectedCategory}
          onChange={(e) => setCategory(e.target.value)}
          className="glass-select"
        >
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>

        {/* Divider */}
        <div className="w-px h-6" style={{ background: 'var(--border)' }} />

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="w-9 h-9 rounded-xl flex items-center justify-center"
          style={{
            color: 'var(--text-secondary)',
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border)',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = 'rgba(var(--accent-rgb),0.3)';
            e.currentTarget.style.boxShadow = '0 0 16px rgba(var(--accent-rgb),0.15)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'var(--border)';
            e.currentTarget.style.boxShadow = 'none';
          }}
          title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
          {theme === 'light' ? <MoonIcon size={16} /> : <SunIcon size={16} />}
        </button>
      </div>
    </header>
  );
}
