/** Number & date formatting utilities */

export function formatCurrency(value, compact = false) {
  if (compact && Math.abs(value) >= 1_000_000) {
    return '$' + (value / 1_000_000).toFixed(1) + 'M';
  }
  if (compact && Math.abs(value) >= 1_000) {
    return '$' + (value / 1_000).toFixed(1) + 'K';
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatNumber(value, decimals = 0) {
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: decimals,
  }).format(value);
}

export function formatPercent(value, decimals = 1) {
  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(decimals)}%`;
}

export function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export function formatDateFull(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}
