'use client';

import { useEffect, useState } from 'react';
import { useDatasetStore } from '@/stores/dataset-store';
import { useRouter } from 'next/navigation';
import { 
  Upload, 
  Database, 
  Trash2, 
  BarChart2, 
  FileText, 
  Loader2, 
  AlertTriangle,
  Info,
  Calendar,
  Layers,
  ArrowRight
} from 'lucide-react';
import { useDropzone } from 'react-dropzone';

export default function DatasetsPage() {
  const router = useRouter();
  const { 
    datasets, 
    isLoading, 
    isUploading, 
    uploadProgress, 
    error, 
    fetchDatasets, 
    uploadDataset, 
    deleteDataset,
    clearError
  } = useDatasetStore();

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  useEffect(() => {
    fetchDatasets();
  }, [fetchDatasets]);

  // Polling for processing/pending datasets
  useEffect(() => {
    const hasProcessing = datasets.some(
      (d) => d.status === 'processing' || d.status === 'pending'
    );
    
    if (!hasProcessing) return;

    const interval = setInterval(() => {
      fetchDatasets();
    }, 3000);

    return () => clearInterval(interval);
  }, [datasets, fetchDatasets]);

  // Dropzone setup
  const onDrop = (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setSelectedFile(file);
      // Auto fill dataset name with filename if empty
      if (!name) {
        setName(file.name.replace(/\.[^/.]+$/, ""));
      }
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    maxFiles: 1,
  });

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    try {
      await uploadDataset(name, description, selectedFile);
      // Reset form
      setName('');
      setDescription('');
      setSelectedFile(null);
    } catch {
      // handled by store
    }
  };

  const handleDelete = async (id: string) => {
    setDeleteId(id);
    try {
      await deleteDataset(id);
    } catch {
      // handled by store
    } finally {
      setDeleteId(null);
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight text-foreground">Datasets Manager</h2>
        <p className="text-foreground/50 font-medium">
          Upload and manage CSV data profiles. Newly uploaded datasets will automatically compile analytics.
        </p>
      </div>

      {/* Error Bar */}
      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 text-sm flex items-start justify-between gap-3">
          <div className="flex gap-3">
            <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
            <span className="font-semibold">{error}</span>
          </div>
          <button onClick={clearError} className="font-bold hover:underline text-xs">Dismiss</button>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid lg:grid-cols-3 gap-8">
        
        {/* Left Column: Upload Panel */}
        <div className="lg:col-span-1 glass-panel p-6 rounded-2xl border border-border h-fit">
          <h3 className="font-bold text-lg text-foreground mb-4 flex items-center gap-2">
            <Upload className="w-5 h-5 text-primary" />
            <span>Upload Dataset</span>
          </h3>

          <form onSubmit={handleUpload} className="space-y-4">
            {/* Drag & Drop zone */}
            <div 
              {...getRootProps()} 
              className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all duration-200 ${
                isDragActive 
                  ? 'border-primary bg-primary/5' 
                  : selectedFile 
                    ? 'border-accent/40 bg-accent/5' 
                    : 'border-border/60 hover:border-primary/50 bg-surface/30'
              }`}
            >
              <input {...getInputProps()} />
              {selectedFile ? (
                <div className="space-y-2">
                  <FileText className="w-10 h-10 text-accent mx-auto" />
                  <span className="font-bold text-sm block truncate text-foreground/80 px-4">{selectedFile.name}</span>
                  <span className="text-xs text-foreground/40 font-medium block">
                    {(selectedFile.size / 1024).toFixed(1)} KB
                  </span>
                </div>
              ) : (
                <div className="space-y-2">
                  <Upload className="w-10 h-10 text-foreground/30 mx-auto" />
                  <span className="font-bold text-sm block text-foreground/70">
                    {isDragActive ? 'Drop your CSV here...' : 'Drag & drop CSV file'}
                  </span>
                  <span className="text-xs text-foreground/40 block">or click to browse local files</span>
                </div>
              )}
            </div>

            {/* Inputs */}
            <div>
              <label className="block text-xs font-semibold text-foreground/50 mb-1.5 uppercase tracking-wider">Dataset Name</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Active Customers Sales"
                className="w-full bg-surface border border-border/80 focus:border-primary rounded-xl py-3 px-4 text-sm outline-none transition-all placeholder:text-foreground/30 font-medium"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-foreground/50 mb-1.5 uppercase tracking-wider">Description (Optional)</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe what data this CSV contains..."
                rows={3}
                className="w-full bg-surface border border-border/80 focus:border-primary rounded-xl py-3 px-4 text-sm outline-none transition-all placeholder:text-foreground/30 font-medium resize-none"
              />
            </div>

            {/* Uploading progress bar */}
            {isUploading && (
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs font-bold text-foreground/60">
                  <span>Uploading to server...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <div className="w-full h-2 bg-border rounded-full overflow-hidden">
                  <div className="h-full bg-primary transition-all duration-300" style={{ width: `${uploadProgress}%` }} />
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={!selectedFile || isUploading}
              className="w-full py-3.5 rounded-xl bg-primary hover:bg-primary-hover disabled:bg-primary/40 text-white font-semibold text-sm transition-all shadow-lg shadow-primary/20 flex items-center justify-center gap-2 cursor-pointer"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing CSV...</span>
                </>
              ) : (
                <span>Upload and Analyze</span>
              )}
            </button>
          </form>
        </div>

        {/* Right Column: Datasets List */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="font-bold text-lg text-foreground flex items-center gap-2 px-1">
            <Database className="w-5 h-5 text-secondary" />
            <span>Active Data Profiles ({datasets.length})</span>
          </h3>

          {isLoading && datasets.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 gap-3 glass-panel rounded-2xl border border-border">
              <Loader2 className="w-8 h-8 text-primary animate-spin" />
              <span className="text-sm font-semibold text-foreground/50">Fetching your datasets...</span>
            </div>
          ) : datasets.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 px-8 text-center glass-panel rounded-2xl border border-border gap-4">
              <Database className="w-12 h-12 text-foreground/20" />
              <div>
                <h4 className="font-bold text-base text-foreground">No datasets uploaded yet</h4>
                <p className="text-foreground/50 text-sm mt-1 max-w-sm">
                  Upload your first CSV dataset using the panel on the left to generate dashboards automatically.
                </p>
              </div>
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 gap-4">
              {datasets.map((dataset) => {
                const isReady = dataset.status === 'ready';
                const isProcessing = dataset.status === 'processing' || dataset.status === 'pending';
                const isError = dataset.status === 'error';

                return (
                  <div 
                    key={dataset.id}
                    className="glass-panel p-5 rounded-2xl border border-border flex flex-col justify-between hover:border-primary/30 transition-all duration-300 group"
                  >
                    <div>
                      {/* Name & status badge */}
                      <div className="flex justify-between items-start gap-3 mb-3">
                        <h4 className="font-bold text-base text-foreground group-hover:text-primary transition-colors truncate">
                          {dataset.name}
                        </h4>
                        
                        {/* Badges */}
                        {isReady && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-500/10 text-green-500 border border-green-500/20">
                            Ready
                          </span>
                        )}
                        {isProcessing && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-500 border border-amber-500/20 animate-pulse">
                            Processing
                          </span>
                        )}
                        {isError && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-500/10 text-red-500 border border-red-500/20">
                            Error
                          </span>
                        )}
                      </div>

                      {/* Row counts & Stats */}
                      <div className="grid grid-cols-2 gap-2 text-xs font-semibold text-foreground/50 mb-4 bg-surface/30 p-2.5 rounded-xl border border-border/50">
                        <div className="flex items-center gap-1.5">
                          <Layers className="w-3.5 h-3.5 text-foreground/40" />
                          <span>Rows: {dataset.rowCount.toLocaleString()}</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <Database className="w-3.5 h-3.5 text-foreground/40" />
                          <span>Cols: {dataset.columnCount}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between mt-2 pt-3 border-t border-border/40 gap-4">
                      {/* Created date */}
                      <span className="text-[10px] font-bold text-foreground/45 flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        <span>{new Date(dataset.createdAt).toLocaleDateString()}</span>
                      </span>

                      {/* Action buttons */}
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleDelete(dataset.id)}
                          disabled={deleteId === dataset.id}
                          className="p-2 rounded-lg border border-border text-foreground/50 hover:text-red-500 hover:bg-red-500/5 transition-colors disabled:opacity-40"
                        >
                          {deleteId === dataset.id ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Trash2 className="w-4 h-4" />
                          )}
                        </button>
                        
                        {isReady && (
                          <button
                            onClick={() => router.push(`/dashboards?datasetId=${dataset.id}`)}
                            className="px-3.5 py-1.5 rounded-lg bg-primary hover:bg-primary-hover text-white font-bold text-xs flex items-center gap-1 transition-all shadow-md shadow-primary/10 cursor-pointer"
                          >
                            <span>Dashboard</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
