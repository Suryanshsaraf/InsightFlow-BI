/**
 * InsightFlow Frontend constants.
 * 
 * Defines global variables used across the frontend,
 * including base API routes, themes, file configurations, and routes.
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const APP_NAME = 'InsightFlow';
export const APP_DESCRIPTION = 'AI-Powered Business Intelligence Platform';

export const CHART_COLORS = [
  '#4361EE', // Electric Blue
  '#7B2FF7', // Vivid Purple
  '#17C3B2', // Teal Green
  '#F72585', // Hot Pink
  '#FFB703', // Amber
  '#4CC9F0', // Sky Blue
  '#3A0CA3', // Deep Purple
  '#F77F00', // Orange
  '#06D6A0', // Mint
  '#EF476F', // Coral
];

export const THEME_COLORS = {
  primary: '#4361EE',
  secondary: '#7B2FF7',
  accent: '#17C3B2',
  danger: '#F72585',
  warning: '#FFB703',
} as const;

export const FILE_TYPES = {
  csv: { label: 'CSV', mime: 'text/csv', extension: '.csv' },
  xlsx: { label: 'Excel', mime: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', extension: '.xlsx' },
  json: { label: 'JSON', mime: 'application/json', extension: '.json' },
  parquet: { label: 'Parquet', mime: 'application/octet-stream', extension: '.parquet' },
} as const;

export const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB

export const ACCEPTED_FILE_TYPES = {
  'text/csv': ['.csv'],
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  'application/json': ['.json'],
  'application/octet-stream': ['.parquet'],
};

export const ROUTES = {
  home: '/',
  login: '/login',
  signup: '/signup',
  datasets: '/datasets',
  datasetDetail: (id: string) => `/datasets/${id}`,
  dashboards: '/dashboards',
  dashboardDetail: (id: string) => `/dashboards/${id}`,
  query: '/query',
  settings: '/settings',
} as const;

export const BREAKPOINTS = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const;
