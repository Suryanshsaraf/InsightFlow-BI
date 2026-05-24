import { create } from 'zustand';
import apiClient from '@/lib/api-client';
import { Dataset, DatasetBrief } from '@/types/dataset';

interface DatasetState {
  datasets: DatasetBrief[];
  activeDataset: Dataset | null;
  isLoading: boolean;
  isUploading: boolean;
  uploadProgress: number;
  error: string | null;
  
  fetchDatasets: () => Promise<void>;
  fetchDatasetDetails: (id: string) => Promise<Dataset>;
  uploadDataset: (name: string, description: string, file: File) => Promise<Dataset>;
  deleteDataset: (id: string) => Promise<void>;
  setActiveDataset: (dataset: Dataset | null) => void;
  clearError: () => void;
}

export const useDatasetStore = create<DatasetState>((set, get) => ({
  datasets: [],
  activeDataset: null,
  isLoading: false,
  isUploading: false,
  uploadProgress: 0,
  error: null,

  fetchDatasets: async () => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await apiClient.get('/datasets/');
      set({ datasets: data, isLoading: false });
    } catch (err: any) {
      set({ error: err.response?.data?.error?.message || 'Failed to fetch datasets', isLoading: false });
    }
  },

  fetchDatasetDetails: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await apiClient.get(`/datasets/${id}`);
      set({ activeDataset: data, isLoading: false });
      return data;
    } catch (err: any) {
      const msg = err.response?.data?.error?.message || 'Failed to fetch dataset details';
      set({ error: msg, isLoading: false });
      throw err;
    }
  },

  uploadDataset: async (name: string, description: string, file: File) => {
    set({ isUploading: true, uploadProgress: 0, error: null });
    
    const formData = new FormData();
    formData.append('name', name);
    if (description) formData.append('description', description);
    formData.append('file', file);

    try {
      const { data } = await apiClient.post('/datasets/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percent = progressEvent.total
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 50;
          set({ uploadProgress: percent });
        },
      });
      
      // Refresh datasets list
      await get().fetchDatasets();
      set({ isUploading: false, uploadProgress: 100 });
      return data;
    } catch (err: any) {
      const msg = err.response?.data?.error?.message || 'Failed to upload dataset';
      set({ error: msg, isUploading: false });
      throw err;
    }
  },

  deleteDataset: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.delete(`/datasets/${id}`);
      set((state) => ({
        datasets: state.datasets.filter((d) => d.id !== id),
        activeDataset: state.activeDataset?.id === id ? null : state.activeDataset,
        isLoading: false,
      }));
    } catch (err: any) {
      set({ error: err.response?.data?.error?.message || 'Failed to delete dataset', isLoading: false });
      throw err;
    }
  },

  setActiveDataset: (dataset) => set({ activeDataset: dataset }),
  clearError: () => set({ error: null }),
}));
