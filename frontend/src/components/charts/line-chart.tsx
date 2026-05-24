'use client';

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { formatAxisTick } from '@/lib/chart-utils';

interface LineChartProps {
  data: Record<string, any>[];
  xField: string;
  yField: string;
  colors?: string[];
  showGrid?: boolean;
}

export default function LineChartComponent({
  data,
  xField,
  yField,
  colors = ['#4361EE'],
  showGrid = true,
}: LineChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-sm text-foreground/50">
        No data available
      </div>
    );
  }

  const primaryColor = colors[0] || '#4361EE';

  return (
    <div className="w-full h-full min-h-[250px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 5 }}>
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
            cursor={{ stroke: 'rgba(255,255,255,0.1)', strokeWidth: 1 }}
          />
          <Line
            type="monotone"
            dataKey={yField}
            stroke={primaryColor}
            strokeWidth={3}
            dot={{ r: 4, stroke: primaryColor, strokeWidth: 1, fill: '#1e293b' }}
            activeDot={{ r: 6, stroke: primaryColor, strokeWidth: 2, fill: '#fff' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
