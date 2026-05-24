'use client';

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { formatAxisTick } from '@/lib/chart-utils';

interface AreaChartProps {
  data: Record<string, any>[];
  xField: string;
  yField: string;
  colors?: string[];
  showGrid?: boolean;
}

export default function AreaChartComponent({
  data,
  xField,
  yField,
  colors = ['#7B2FF7'],
  showGrid = true,
}: AreaChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-sm text-foreground/50">
        No data available
      </div>
    );
  }

  const primaryColor = colors[0] || '#7B2FF7';
  const gradientId = `colorUv-${xField}-${yField}`;

  return (
    <div className="w-full h-full min-h-[250px]">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 5 }}>
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={primaryColor} stopOpacity={0.3} />
              <stop offset="95%" stopColor={primaryColor} stopOpacity={0.0} />
            </linearGradient>
          </defs>
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
          <Area
            type="monotone"
            dataKey={yField}
            stroke={primaryColor}
            strokeWidth={3}
            fillOpacity={1}
            fill={`url(#${gradientId})`}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
