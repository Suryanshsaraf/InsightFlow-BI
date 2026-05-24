export interface Insight {
  id: string;
  dashboardId: string;
  type: InsightType;
  title: string;
  description: string;
  severity: 'info' | 'warning' | 'critical' | 'positive';
  confidence: number;
  relatedChartId?: string;
  relatedMetric?: string;
  suggestedAction?: string;
  createdAt: string;
  metadata?: Record<string, unknown>;
}

export type InsightType =
  | 'anomaly'
  | 'trend'
  | 'correlation'
  | 'forecast'
  | 'recommendation'
  | 'summary';

export interface InsightFilter {
  types?: InsightType[];
  severity?: Insight['severity'][];
  minConfidence?: number;
}

export interface QueryResult {
  columns: string[];
  rows: Record<string, unknown>[];
  rowCount: number;
  executionTimeMs: number;
  query: string;
}

export interface QueryHistoryItem {
  id: string;
  query: string;
  executedAt: string;
  executionTimeMs: number;
  rowCount: number;
  status: 'success' | 'error';
  error?: string;
  datasetId?: string;
}

export interface NLQueryRequest {
  question: string;
  datasetId?: string;
  context?: string;
}

export interface NLQueryResponse {
  sql: string;
  explanation: string;
  result: QueryResult;
  confidence: number;
}
