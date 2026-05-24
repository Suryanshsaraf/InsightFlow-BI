'use client';

import { useAuthStore } from '@/stores/auth-store';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, isLoading } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    // Redirect to dashboards if already authenticated
    if (isAuthenticated) {
      router.push('/dashboards');
    }
  }, [isAuthenticated, router]);

  return (
    <div className="min-h-screen bg-background relative flex items-center justify-center py-12 px-6 overflow-hidden">
      {/* Glow decorative blobs */}
      <div className="absolute top-[20%] left-[20%] w-[40%] h-[40%] rounded-full bg-primary/10 blur-[130px] pointer-events-none" />
      <div className="absolute bottom-[20%] right-[20%] w-[40%] h-[40%] rounded-full bg-secondary/10 blur-[130px] pointer-events-none" />
      
      <div className="w-full max-w-md z-10">
        {children}
      </div>
    </div>
  );
}
