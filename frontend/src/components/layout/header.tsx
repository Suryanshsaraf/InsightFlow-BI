'use client';

import { usePathname } from 'next/navigation';
import { Sun, Moon, Bell } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function Header() {
  const pathname = usePathname();
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // Check initial state
    const root = window.document.documentElement;
    const initialDark = root.classList.contains('dark');
    setIsDark(initialDark);
  }, []);

  const toggleTheme = () => {
    const root = window.document.documentElement;
    if (isDark) {
      root.classList.remove('dark');
      localStorage.setItem('theme', 'light');
      setIsDark(false);
    } else {
      root.classList.add('dark');
      localStorage.setItem('theme', 'dark');
      setIsDark(true);
    }
  };

  // Generate page title from path
  const getPageTitle = () => {
    if (pathname === '/dashboards') return 'Dashboards';
    if (pathname.startsWith('/dashboards/')) return 'Dashboard Analytics';
    if (pathname.startsWith('/datasets')) return 'Datasets';
    if (pathname === '/query') return 'Query Workbench';
    return 'Analytics';
  };

  return (
    <header className="h-16 border-b border-border bg-surface/50 backdrop-blur-md flex items-center justify-between px-8 sticky top-0 z-10">
      <div>
        <h1 className="font-semibold text-lg text-foreground tracking-tight">{getPageTitle()}</h1>
      </div>

      <div className="flex items-center gap-4">
        {/* Notifications */}
        <button className="p-2 rounded-xl text-foreground/60 hover:text-foreground hover:bg-surface-hover transition-colors border border-border bg-surface">
          <Bell className="w-4 h-4" />
        </button>

        {/* Theme Toggler */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-xl text-foreground/60 hover:text-foreground hover:bg-surface-hover transition-colors border border-border bg-surface"
        >
          {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>
      </div>
    </header>
  );
}
