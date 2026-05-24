'use client';

import Link from 'next/link';
import { useAuthStore } from '@/stores/auth-store';
import { 
  LineChart, 
  ArrowRight, 
  Upload, 
  Cpu, 
  Sparkles, 
  Database, 
  Lock,
  BarChart3,
  TrendingUp,
  BrainCircuit
} from 'lucide-react';

export default function Home() {
  const { isAuthenticated } = useAuthStore();

  return (
    <div className="min-h-screen bg-background relative overflow-hidden flex flex-col justify-between">
      
      {/* Background Decorative Gradients */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-secondary/10 blur-[120px] pointer-events-none" />
      
      {/* Header / Nav */}
      <header className="w-full max-w-7xl mx-auto px-8 h-20 flex items-center justify-between z-10 relative">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-primary to-secondary flex items-center justify-center shadow-lg shadow-primary/20">
            <LineChart className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-xl bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            InsightFlow
          </span>
        </div>
        <div className="flex items-center gap-4">
          {isAuthenticated ? (
            <Link 
              href="/dashboards" 
              className="px-5 py-2.5 rounded-xl bg-primary text-white hover:bg-primary-hover font-semibold text-sm transition-all shadow-lg shadow-primary/20 flex items-center gap-2"
            >
              <span>Go to Console</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          ) : (
            <>
              <Link href="/login" className="text-foreground/70 hover:text-foreground font-semibold text-sm transition-colors">
                Sign In
              </Link>
              <Link 
                href="/signup" 
                className="px-5 py-2.5 rounded-xl bg-primary text-white hover:bg-primary-hover font-semibold text-sm transition-all shadow-lg shadow-primary/20"
              >
                Get Started
              </Link>
            </>
          )}
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-8 pt-16 pb-20 flex flex-col items-center justify-center text-center relative z-10 flex-1">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-border/80 bg-surface/40 backdrop-blur-md mb-8 hover:bg-surface-hover/50 transition-all cursor-pointer">
          <Sparkles className="w-4 h-4 text-secondary" />
          <span className="text-xs font-semibold text-foreground/80">AI-Powered Business Intelligence</span>
        </div>

        <h1 className="max-w-4xl text-5xl md:text-7xl font-extrabold tracking-tight leading-[1.1] mb-6">
          Upload CSV. <br />
          <span className="bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
            Instantly Understand
          </span> Your Data.
        </h1>

        <p className="max-w-2xl text-foreground/60 text-lg md:text-xl mb-12 font-medium leading-relaxed">
          The ultimate zero-setup analytics tool. Drop your files to auto-generate beautiful interactive dashboards, query in plain English, and stream instant AI insights.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 mb-20 w-full justify-center">
          <Link 
            href={isAuthenticated ? "/dashboards" : "/signup"} 
            className="px-8 py-4 rounded-xl bg-primary text-white hover:bg-primary-hover font-semibold text-base transition-all shadow-xl shadow-primary/20 flex items-center justify-center gap-2"
          >
            <span>Start Free Trial</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
          <Link 
            href="/login" 
            className="px-8 py-4 rounded-xl border border-border bg-surface hover:bg-surface-hover text-foreground font-semibold text-base transition-all flex items-center justify-center gap-2"
          >
            <span>Interactive Demo</span>
          </Link>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid md:grid-cols-3 gap-8 w-full">
          <div className="glass-panel p-8 rounded-2xl text-left hover:scale-[1.02] transition-all duration-300">
            <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary mb-6">
              <Upload className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-lg text-foreground mb-3">Auto-Layout Engine</h3>
            <p className="text-foreground/50 text-sm leading-relaxed">
              Drop any CSV dataset. Our system handles data parsing, type inference, schema isolation, and recommends optimal layouts instantly.
            </p>
          </div>

          <div className="glass-panel p-8 rounded-2xl text-left hover:scale-[1.02] transition-all duration-300">
            <div className="w-12 h-12 rounded-xl bg-secondary/10 flex items-center justify-center text-secondary mb-6">
              <BrainCircuit className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-lg text-foreground mb-3">NL to SQL Queries</h3>
            <p className="text-foreground/50 text-sm leading-relaxed">
              Don't know SQL? Write inquiries in plain English. Our GPT-4o integration translates prompts to safe SQL queries and renders tables instantly.
            </p>
          </div>

          <div className="glass-panel p-8 rounded-2xl text-left hover:scale-[1.02] transition-all duration-300">
            <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center text-accent mb-6">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-lg text-foreground mb-3">AI Executive Insights</h3>
            <p className="text-foreground/50 text-sm leading-relaxed">
              Receive smart summaries highlighting outliers, correlations, trend directions, and performance ratios of your dataset automatically.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full max-w-7xl mx-auto px-8 h-20 border-t border-border flex items-center justify-between text-xs text-foreground/40 z-10 relative">
        <span>© 2026 InsightFlow. All rights reserved.</span>
        <div className="flex gap-6">
          <a href="#" className="hover:text-foreground">Privacy Policy</a>
          <a href="#" className="hover:text-foreground">Terms of Service</a>
        </div>
      </footer>
    </div>
  );
}
