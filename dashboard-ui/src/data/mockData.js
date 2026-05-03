/** Mock data generators — realistic M5-style demand data */

const STORES = ['CA_1', 'CA_2', 'CA_3', 'CA_4', 'TX_1', 'TX_2', 'TX_3', 'WI_1', 'WI_2', 'WI_3'];
const CATEGORIES = ['FOODS', 'HOUSEHOLD', 'HOBBIES'];
const DEPARTMENTS = ['FOODS_1', 'FOODS_2', 'FOODS_3', 'HOBBIES_1', 'HOBBIES_2', 'HOUSEHOLD_1', 'HOUSEHOLD_2'];

function seededRandom(seed) {
  let s = seed;
  return () => {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
}

function generateDates(days, endDate = new Date()) {
  const dates = [];
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(endDate);
    d.setDate(d.getDate() - i);
    dates.push(d.toISOString().split('T')[0]);
  }
  return dates;
}

export function generateForecastData(horizon = 28) {
  const rng = seededRandom(42);
  const today = new Date();
  const historicalDays = 90;

  const histDates = generateDates(historicalDays, today);
  const forecastDates = [];
  for (let i = 1; i <= horizon; i++) {
    const d = new Date(today);
    d.setDate(d.getDate() + i);
    forecastDates.push(d.toISOString().split('T')[0]);
  }

  const historical = histDates.map((date, i) => {
    const base = 45 + Math.sin(i / 7 * Math.PI) * 12;
    const trend = i * 0.08;
    const noise = (rng() - 0.5) * 15;
    return {
      date,
      actual: Math.max(0, Math.round(base + trend + noise)),
      forecast: null,
      upper: null,
      lower: null,
    };
  });

  const lastActual = historical[historical.length - 1].actual;
  const forecast = forecastDates.map((date, i) => {
    const base = lastActual + Math.sin((i + historicalDays) / 7 * Math.PI) * 10;
    const trend = i * 0.15;
    const fc = Math.max(0, Math.round(base + trend + (rng() - 0.5) * 8));
    return {
      date,
      actual: null,
      forecast: fc,
      upper: Math.round(fc * 1.25),
      lower: Math.round(fc * 0.78),
    };
  });

  return [...historical, ...forecast];
}

export function generateKPIData() {
  return {
    totalRevenue: { value: 2847300, change: 8.4, label: 'Total Revenue', prefix: '$' },
    forecastAccuracy: { value: 94.2, change: 1.8, label: 'Forecast Accuracy', suffix: '%' },
    promotionLift: { value: 15.6, change: 3.2, label: 'Promotion Lift', suffix: '%' },
    anomalyCount: { value: 12, change: -25, label: 'Anomalies (24h)', isAnomaly: true },
    avgPriceChange: { value: 4.7, change: 0.8, label: 'Avg Price Δ', suffix: '%' },
  };
}

export function generatePromotionData() {
  const rng = seededRandom(123);
  const categories = ['FOODS_1', 'FOODS_2', 'FOODS_3', 'HOBBIES_1', 'HOUSEHOLD_1'];
  return categories.map(cat => {
    const baseline = 800 + rng() * 400;
    const lift = 1 + rng() * 0.35;
    return {
      category: cat,
      baseline: Math.round(baseline),
      promoted: Math.round(baseline * lift),
      lift: Math.round((lift - 1) * 100 * 10) / 10,
    };
  });
}

export function generatePricingData() {
  const rng = seededRandom(99);
  const prices = [];
  for (let m = 0.75; m <= 1.30; m += 0.05) {
    const elasticity = -1.5;
    const baseDemand = 150;
    const basePrice = 3.99;
    const price = Math.round(basePrice * m * 100) / 100;
    const demand = Math.round(baseDemand * Math.pow(m, elasticity));
    const revenue = Math.round(price * demand);
    prices.push({ multiplier: Math.round(m * 100) / 100, price, demand, revenue });
  }
  return {
    currentPrice: 3.99,
    recommendedPrice: 3.59,
    optimalMultiplier: 0.90,
    revenueCurve: prices,
    expectedLift: 8.4,
    confidence: 0.92,
  };
}

export function generateAnomalyData() {
  const rng = seededRandom(77);
  const dates = generateDates(180);
  const data = dates.map((date, i) => {
    const base = 50 + Math.sin(i / 7 * Math.PI) * 15;
    const trend = i * 0.05;
    const value = Math.max(0, Math.round(base + trend + (rng() - 0.5) * 12));
    return { date, value, isAnomaly: false, score: 0 };
  });

  // Inject anomalies at specific points
  const anomalyIndices = [23, 56, 89, 112, 134, 145, 167];
  anomalyIndices.forEach(idx => {
    if (idx < data.length) {
      const spike = rng() > 0.5;
      data[idx].value = spike ? data[idx].value * 3.2 : Math.round(data[idx].value * 0.15);
      data[idx].isAnomaly = true;
      data[idx].score = Math.round((rng() * 2 + 2.5) * 100) / 100;
      data[idx].reason = spike ? 'Demand spike — likely stockout recovery' : 'Sharp drop — possible data error';
    }
  });

  return data;
}

export function generateDemandTrend() {
  const rng = seededRandom(55);
  return generateDates(30).map((date, i) => ({
    date,
    foods: Math.round(120 + Math.sin(i / 5) * 25 + (rng() - 0.5) * 15),
    household: Math.round(85 + Math.cos(i / 6) * 18 + (rng() - 0.5) * 10),
    hobbies: Math.round(45 + Math.sin(i / 4) * 12 + (rng() - 0.5) * 8),
  }));
}

export { STORES, CATEGORIES, DEPARTMENTS };
