'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';
import { signup } from '@/lib/auth';
import { LineChart, Lock, Mail, User as UserIcon, Loader2, AlertCircle } from 'lucide-react';

export default function SignupPage() {
  const router = useRouter();
  const loginStore = useAuthStore((state) => state.login);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const data = await signup({ name, email, password });
      
      // Save in zustand store
      loginStore(data.user, data.tokens.accessToken, data.tokens.refreshToken);
      
      router.push('/dashboards');
    } catch (err: any) {
      setError(
        err.response?.data?.error?.message || 
        'Failed to register account. Please check details.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="glass-panel p-8 rounded-2xl border border-border shadow-2xl relative">
      
      {/* Brand Header */}
      <div className="flex flex-col items-center mb-8">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-primary to-secondary flex items-center justify-center shadow-lg shadow-primary/20 mb-3">
          <LineChart className="w-6 h-6 text-white" />
        </div>
        <h2 className="text-2xl font-bold text-foreground">Create Account</h2>
        <p className="text-xs text-foreground/50 mt-1 font-medium">
          Get started with a free sandbox account
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 text-sm flex items-start gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
          <span className="font-medium">{error}</span>
        </div>
      )}

      {/* Signup Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-foreground/60 mb-1.5 uppercase tracking-wider">
            Full Name
          </label>
          <div className="relative">
            <UserIcon className="absolute left-3.5 top-3.5 w-5 h-5 text-foreground/45" />
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Sarah Jenkins"
              className="w-full bg-surface border border-border/80 focus:border-primary rounded-xl py-3 pl-11 pr-4 text-sm outline-none transition-all placeholder:text-foreground/30 font-medium"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-foreground/60 mb-1.5 uppercase tracking-wider">
            Email Address
          </label>
          <div className="relative">
            <Mail className="absolute left-3.5 top-3.5 w-5 h-5 text-foreground/45" />
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="sarah@company.com"
              className="w-full bg-surface border border-border/80 focus:border-primary rounded-xl py-3 pl-11 pr-4 text-sm outline-none transition-all placeholder:text-foreground/30 font-medium"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-foreground/60 mb-1.5 uppercase tracking-wider">
            Password (min 8 chars)
          </label>
          <div className="relative">
            <Lock className="absolute left-3.5 top-3.5 w-5 h-5 text-foreground/45" />
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-surface border border-border/80 focus:border-primary rounded-xl py-3 pl-11 pr-4 text-sm outline-none transition-all placeholder:text-foreground/30 font-medium"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-3.5 rounded-xl bg-primary hover:bg-primary-hover disabled:bg-primary/50 text-white font-semibold text-sm transition-all shadow-lg shadow-primary/20 flex items-center justify-center gap-2 cursor-pointer"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Creating Account...</span>
            </>
          ) : (
            <span>Sign Up</span>
          )}
        </button>
      </form>

      {/* Toggle Link */}
      <div className="text-center mt-6 text-sm text-foreground/50">
        Already have an account?{' '}
        <Link href="/login" className="text-primary hover:underline font-semibold transition-all">
          Sign in
        </Link>
      </div>
    </div>
  );
}
