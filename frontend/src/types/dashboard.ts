import { ChartConfig } from './chart';

export interface Dashboard {
  id: string;
  name: string;
  description: string;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  isPublic: boolean;
  tags: string[];
  thumbnail?: string;
  datasetId: string;
  kpis: KPIConfig[];
  charts: DashboardChart[];
  filters: DashboardFilter[];
  layout: LayoutItem[];
}

export interface KPIConfig {
  id: string;
  title: string;
  value: number;
  previousValue?: number;
  format: 'number' | 'currency' | 'percentage';
  prefix?: string;
  suffix?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: number;
  icon?: string;
  color?: string;
  datasetId?: string;
  query?: string;
}

export interface DashboardChart {
  id: string;
  chartConfig: ChartConfig;
  data: Record<string, unknown>[];
}

export interface DashboardFilter {
  id: string;
  label: string;
  field: string;
  type: 'select' | 'multiselect' | 'daterange' | 'range' | 'search';
  options?: FilterOption[];
  defaultValue?: string | string[] | number | [number, number];
  datasetId?: string;
}

export interface FilterOption {
  label: string;
  value: string;
}

export interface LayoutItem {
  i: string;
  x: number;
  y: number;
  w: number;
  h: number;
  minW?: number;
  minH?: number;
  maxW?: number;
  maxH?: number;
  static?: boolean;
}

export interface DashboardCreateRequest {
  name: string;
  description?: string;
  isPublic?: boolean;
  tags?: string[];
}
