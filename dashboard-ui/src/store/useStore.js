import { create } from 'zustand';

const useStore = create((set) => ({
  // Theme
  theme: window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
  toggleTheme: () =>
    set((state) => {
      const next = state.theme === 'light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', next);
      return { theme: next };
    }),

  // Filters
  selectedStore: 'CA_1',
  selectedCategory: 'FOODS',
  dateRange: '30d',
  setStore: (store) => set({ selectedStore: store }),
  setCategory: (cat) => set({ selectedCategory: cat }),
  setDateRange: (range) => set({ dateRange: range }),

  // Loading states
  loading: {
    kpi: true,
    forecast: true,
    pricing: true,
    anomaly: true,
    promotion: true,
  },
  setLoading: (key, val) =>
    set((state) => ({ loading: { ...state.loading, [key]: val } })),

  // Sidebar
  sidebarExpanded: false,
  setSidebarExpanded: (val) => set({ sidebarExpanded: val }),
}));

export default useStore;
