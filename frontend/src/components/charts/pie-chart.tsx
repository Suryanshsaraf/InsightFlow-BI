'use client';

import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from 'recharts';

interface PieChartProps {
  data: Record<string, any>[];
  xField: string;
  yField: string;
  colors?: string[];
  innerRadius?: number;
}

const DEFAULT_COLORS = [
  '#4361EE',
  '#7B2FF7',
  '#17C3B2',
  '#F72585',
  '#FFB703',
  '#3F37C9',
];

export default function PieChartComponent({
  data,
  xField,
  yField,
  colors = DEFAULT_COLORS,
  innerRadius = 0,
}: PieChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-sm text-foreground/50">
        No data available
      </div>
    );
  }

  // Ensure data counts / sums are numeric
  const processedData = data.map((item) => ({
    ...item,
    [yField]: Number(item[yField]),
  }));

  return (
    <div className="w-full h-full min-h-[250px] flex items-center justify-center">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
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
          />
          <Legend
            verticalAlign="bottom"
            height={36}
            iconType="circle"
            iconSize={8}
            formatter={(value) => (
              <span className="text-xs text-foreground/70 font-medium px-1">
                {value}
              </span>
            )}
          />
          <Pie
            data={processedData}
            cx="50%"
            cy="45%"
            labelLine={false}
            outerRadius={80}
            innerRadius={innerRadius}
            fill="#8884d8"
            dataKey={yField}
            nameKey={xField}
          >
            {processedData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={colors[index % colors.length]}
                stroke="rgba(15, 23, 42, 0.8)"
                strokeWidth={2}
              />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
