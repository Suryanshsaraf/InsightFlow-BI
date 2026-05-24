export interface Dataset {
  id: string;
  name: string;
  description: string;
  fileName: string;
  fileSize: number;
  fileType: 'csv' | 'xlsx' | 'json' | 'parquet';
  rowCount: number;
  columnCount: number;
  columns: DatasetColumn[];
  status: 'uploading' | 'processing' | 'ready' | 'error' | 'pending';
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  tags: string[];
  previewData?: Record<string, unknown>[];
}

export interface DatasetColumn {
  name: string;
  type: 'string' | 'number' | 'date' | 'boolean';
  nullable: boolean;
  uniqueCount?: number;
  sampleValues?: (string | number | boolean | null)[];
  stats?: ColumnStats;
}

export interface ColumnStats {
  min?: number;
  max?: number;
  mean?: number;
  median?: number;
  stdDev?: number;
  nullCount: number;
  distinctCount: number;
}

export interface DatasetUploadProgress {
  datasetId: string;
  fileName: string;
  progress: number;
  status: 'uploading' | 'processing' | 'complete' | 'error';
  error?: string;
}

export interface DatasetCreateRequest {
  name: string;
  description?: string;
  tags?: string[];
  file: File;
}

export interface DatasetBrief {
  id: string;
  name: string;
  status: 'uploading' | 'processing' | 'ready' | 'error' | 'pending';
  rowCount: number;
  columnCount: number;
  createdAt: string;
}

