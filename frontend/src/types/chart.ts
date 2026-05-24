export type ChartType = 'line' | 'bar' | 'pie' | 'area' | 'table';

export interface ChartConfig {
  id: string;
  type: ChartType;
  title: string;
  description?: string;
  datasetId: string;
  xAxis?: AxisConfig;
  yAxis?: AxisConfig;
  series: SeriesConfig[];
  colorScheme?: string[];
  showLegend?: boolean;
  showGrid?: boolean;
  stacked?: boolean;
  animated?: boolean;
}

export interface AxisConfig {
  field: string;
  label?: string;
  format?: string;
  tickCount?: number;
}

export interface SeriesConfig {
  field: string;
  label: string;
  color?: string;
  type?: 'line' | 'bar' | 'area';
}

export interface ChartDataPoint {
  [key: string]: string | number | null;
}

export interface ChartTheme {
  colors: string[];
  backgroundColor: string;
  gridColor: string;
  textColor: string;
  fontSize: number;
  fontFamily: string;
}
