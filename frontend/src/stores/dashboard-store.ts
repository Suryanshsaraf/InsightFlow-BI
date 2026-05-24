import { create } from 'zustand';
import apiClient from '@/lib/api-client';
import { Dashboard, LayoutItem } from '@/types/dashboard';

interface DashboardState {
  dashboards: Dashboard[];
  activeDashboard: Dashboard | null;
  activeFilters: Record<string, any>[]; // List of active interactive filters
  isLoading: boolean;
  error: string | null;

  fetchDashboards: () => Promise<void>;
  fetchDashboardDetails: (id: string) => Promise<Dashboard>;
  updateDashboardLayout: (id: string, layout: LayoutItem[]) => Promise<void>;
  deleteDashboard: (id: string) => Promise<void>;
  applyFilters: (filters: Record<string, any>[]) => void;
  clearFilters: () => void;
  clearError: () => void;
}

export const useDashboardStore = create<DashboardState>((set, get) => ({
  dashboards: [],
  activeDashboard: null,
  activeFilters: [],
  isLoading: false,
  error: null,

  fetchDashboards: async () => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await apiClient.get('/dashboards/');
      set({ dashboards: data, isLoading: false });
    } catch (err: any) {
      set({ error: err.response?.data?.error?.message || 'Failed to fetch dashboards', isLoading: false });
    }
  },

  fetchDashboardDetails: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await apiClient.get(`/dashboards/${id}`);
      set({ activeDashboard: data, isLoading: false });
      return data;
    } catch (err: any) {
      const msg = err.response?.data?.error?.message || 'Failed to fetch dashboard details';
      set({ error: msg, isLoading: false });
      throw err;
    }
  },

  updateDashboardLayout: async (id: string, layout: LayoutItem[]) => {
    try {
      // Map LayoutItem[] to layoutConfig
      const layoutConfig = { items: layout };
      const { data } = await apiClient.put(`/dashboards/${id}`, {
        layoutConfig,
      });
      set({ activeDashboard: data });
    } catch (err: any) {
      set({ error: err.response?.data?.error?.message || 'Failed to update layout' });
    }
  },

  deleteDashboard: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.delete(`/dashboards/${id}`);
      set((state) => ({
        dashboards: state.dashboards.filter((d) => d.id !== id),
        activeDashboard: state.activeDashboard?.id === id ? null : state.activeDashboard,
        isLoading: false,
      }));
    } catch (err: any) {
      set({ error: err.response?.data?.error?.message || 'Failed to delete dashboard', isLoading: false });
      throw err;
    }
  },

  applyFilters: (filters) => {
    set({ activeFilters: filters });
  },

  clearFilters: () => {
    set({ activeFilters: [] });
  },

  clearError: () => set({ error: null }),
}));
