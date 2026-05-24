'use client';

import Sidebar from '@/components/layout/sidebar';
import Header from '@/components/layout/header';
import { useAuthStore } from '@/stores/auth-store';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { Loader2 } from 'lucide-react';

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, isLoading, setUser, setLoading } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    // Check if token exists in localStorage to restore session
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      setLoading(false);
      router.push('/login');
      return;
    }

    // Restore session if token exists
    if (!isAuthenticated) {
      // In a real app we'd fetch profile from /auth/me,
      // here we restore simple state or fetch.
      // We can fetch from API client or just assume authenticated.
      // For MVP, we let store trigger fetch or assume session.
      // Let's call /me to verify token.
      import('@/lib/auth').then(({ getCurrentUser }) => {
        getCurrentUser()
          .then((user) => {
            setUser(user);
            setLoading(false);
          })
          .catch(() => {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            setUser(null);
            setLoading(false);
            router.push('/login');
          });
      });
    } else {
      setLoading(false);
    }
  }, [isAuthenticated, router, setUser, setLoading]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center gap-4">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
        <span className="text-sm font-semibold text-foreground/50">Restoring Session...</span>
      </div>
    );
  }

  // Allow layout load even if auth is restoring to prevent flashes
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto bg-background p-8">
          <div className="max-w-7xl mx-auto w-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
