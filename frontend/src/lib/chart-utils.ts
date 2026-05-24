import { ChartTheme } from '@/types/chart';
import { CHART_COLORS } from './constants';

export const darkChartTheme: ChartTheme = {
  colors: CHART_COLORS,
  backgroundColor: 'transparent',
  gridColor: 'rgba(255, 255, 255, 0.06)',
  textColor: 'rgba(255, 255, 255, 0.6)',
  fontSize: 12,
  fontFamily: 'Inter, system-ui, sans-serif',
};

export const lightChartTheme: ChartTheme = {
  colors: CHART_COLORS,
  backgroundColor: 'transparent',
  gridColor: 'rgba(0, 0, 0, 0.06)',
  textColor: 'rgba(0, 0, 0, 0.6)',
  fontSize: 12,
  fontFamily: 'Inter, system-ui, sans-serif',
};

export function getChartColor(index: number, colors: string[] = CHART_COLORS): string {
  return colors[index % colors.length];
}

export function generateGradientId(chartId: string, index: number): string {
  return `gradient-${chartId}-${index}`;
}

export function formatAxisTick(value: number): string {
  if (Math.abs(value) >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (Math.abs(value) >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return value.toString();
}

export function calculateTrendPercentage(current: number, previous: number): number {
  if (previous === 0) return current > 0 ? 100 : 0;
  return ((current - previous) / Math.abs(previous)) * 100;
}

export function getTrendDirection(current: number, previous: number): 'up' | 'down' | 'neutral' {
  const diff = current - previous;
  if (Math.abs(diff) < 0.001) return 'neutral';
  return diff > 0 ? 'up' : 'down';
}

export const chartMargins = {
  top: 20,
  right: 20,
  bottom: 20,
  left: 20,
};

export const tooltipStyles = {
  dark: {
    contentStyle: {
      backgroundColor: 'rgba(15, 15, 20, 0.95)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '12px',
      padding: '12px 16px',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
      backdropFilter: 'blur(20px)',
    },
    labelStyle: {
      color: 'rgba(255, 255, 255, 0.7)',
      fontWeight: 500,
      marginBottom: '4px',
    },
    itemStyle: {
      color: 'rgba(255, 255, 255, 0.9)',
      fontSize: '13px',
    },
  },
  light: {
    contentStyle: {
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      border: '1px solid rgba(0, 0, 0, 0.08)',
      borderRadius: '12px',
      padding: '12px 16px',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
      backdropFilter: 'blur(20px)',
    },
    labelStyle: {
      color: 'rgba(0, 0, 0, 0.6)',
      fontWeight: 500,
      marginBottom: '4px',
    },
    itemStyle: {
      color: 'rgba(0, 0, 0, 0.8)',
      fontSize: '13px',
    },
  },
};
