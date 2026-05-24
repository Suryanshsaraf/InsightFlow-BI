'use client';

import dynamic from 'next/dynamic';
import { ChartType } from '@/types/chart';

// Lazy load chart components to keep the initial bundle small
const LineChart = dynamic(() => import('./line-chart'), { ssr: false });
const BarChart = dynamic(() => import('./bar-chart'), { ssr: false });
const PieChart = dynamic(() => import('./pie-chart'), { ssr: false });
const AreaChart = dynamic(() => import('./area-chart'), { ssr: false });
const DataTable = dynamic(() => import('./data-table'), { ssr: false });

interface ChartRendererProps {
  type: ChartType | 'donut';
  data: Record<string, any>[];
  xField?: string;
  yField?: string;
  colors?: string[];
  showGrid?: boolean;
}

export default function ChartRenderer({
  type,
  data,
  xField,
  yField,
  colors,
  showGrid = true,
}: ChartRendererProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-sm text-foreground/40 font-medium">
        No data available to display this chart.
      </div>
    );
  }

  // Ensure fields exist for aggregated visual charts
  if (type !== 'table' && (!xField || !yField)) {
    return (
      <div className="h-full flex items-center justify-center text-sm text-danger/70 font-medium p-6 text-center">
        Invalid configuration: X and Y fields are required.
      </div>
    );
  }

  switch (type) {
    case 'line':
      return (
        <LineChart
          data={data}
          xField={xField!}
          yField={yField!}
          colors={colors}
          showGrid={showGrid}
        />
      );
    case 'bar':
      return (
        <BarChart
          data={data}
          xField={xField!}
          yField={yField!}
          colors={colors}
          showGrid={showGrid}
        />
      );
    case 'pie':
      return (
        <PieChart
          data={data}
          xField={xField!}
          yField={yField!}
          colors={colors}
        />
      );
    case 'donut':
      return (
        <PieChart
          data={data}
          xField={xField!}
          yField={yField!}
          colors={colors}
          innerRadius={60}
        />
      );
    case 'area':
      return (
        <AreaChart
          data={data}
          xField={xField!}
          yField={yField!}
          colors={colors}
          showGrid={showGrid}
        />
      );
    case 'table':
      return <DataTable data={data} />;
    default:
      return <DataTable data={data} />;
  }
}
