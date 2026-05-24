/**
 * Authentication client module.
 * Handles api routing for logins, signups, and storage of JWT tokens.
 */
import apiClient from './api-client';
import { User, LoginRequest, SignupRequest, AuthTokens } from '@/types/api';

export async function login(credentials: LoginRequest): Promise<{ user: User; tokens: AuthTokens }> {
  const { data } = await apiClient.post('/auth/login', credentials);
  return data;
}

export async function signup(request: SignupRequest): Promise<{ user: User; tokens: AuthTokens }> {
  const { data } = await apiClient.post('/auth/signup', request);
  return data;
}

export async function logout(): Promise<void> {
  try {
    await apiClient.post('/auth/logout');
  } finally {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}

export async function getCurrentUser(): Promise<User> {
  const { data } = await apiClient.get('/auth/me');
  return data;
}

export function saveTokens(tokens: AuthTokens): void {
  localStorage.setItem('access_token', tokens.accessToken);
  localStorage.setItem('refresh_token', tokens.refreshToken);
}

export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

export function isAuthenticated(): boolean {
  return !!getAccessToken();
}
