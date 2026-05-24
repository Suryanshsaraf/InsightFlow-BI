'use client';

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { formatAxisTick } from '@/lib/chart-utils';

interface BarChartProps {
  data: Record<string, any>[];
  xField: string;
  yField: string;
  colors?: string[];
  showGrid?: boolean;
}

export default function BarChartComponent({
  data,
  xField,
  yField,
  colors = ['#17C3B2'],
  showGrid = true,
}: BarChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-sm text-foreground/50">
        No data available
      </div>
    );
  }

  const primaryColor = colors[0] || '#17C3B2';

  return (
    <div className="w-full h-full min-h-[250px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 5 }}>
          {showGrid && (
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
          )}
          <XAxis
            dataKey={xField}
            stroke="rgba(255,255,255,0.4)"
            fontSize={11}
            tickLine={false}
            axisLine={false}
            dy={8}
          />
          <YAxis
            stroke="rgba(255,255,255,0.4)"
            fontSize={11}
            tickLine={false}
            axisLine={false}
            tickFormatter={formatAxisTick}
            dx={-8}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(15, 23, 42, 0.95)',
              borderColor: 'rgba(255, 255, 255, 0.1)',
              borderRadius: '12px',
              color: '#fff',
              fontSize: '12px',
              boxShadow: '0 10px 25px -5px rgba(0,0,0,0.5)',
            }}
            itemStyle={{ color: '#fff' }}
            cursor={{ fill: 'rgba(255, 255, 255, 0.04)' }}
          />
          <Bar
            dataKey={yField}
            fill={primaryColor}
            radius={[4, 4, 0, 0]}
            maxBarSize={50}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
