'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';
import { 
  LayoutDashboard, 
  Database, 
  Code2, 
  LogOut, 
  LineChart,
  User as UserIcon,
  ChevronsLeftRight
} from 'lucide-react';
import { logout } from '@/lib/auth';

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout: logoutStore } = useAuthStore();

  const navItems = [
    {
      name: 'Dashboards',
      href: '/dashboards',
      icon: LayoutDashboard,
    },
    {
      name: 'Datasets',
      href: '/datasets',
      icon: Database,
    },
    {
      name: 'Query Editor',
      href: '/query',
      icon: Code2,
    },
  ];

  const handleLogout = async () => {
    await logout();
    logoutStore();
    router.push('/login');
  };

  return (
    <aside className="w-64 bg-surface border-r border-border flex flex-col h-screen sticky top-0">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 gap-3 border-b border-border">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-primary to-secondary flex items-center justify-center">
          <LineChart className="w-5 h-5 text-white" />
        </div>
        <div>
          <span className="font-bold text-lg bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            InsightFlow
          </span>
          <span className="text-[10px] block text-muted-foreground font-semibold tracking-wider uppercase">
            Platform MVP
          </span>
        </div>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 py-6 px-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
                isActive
                  ? 'bg-primary text-white shadow-lg shadow-primary/20'
                  : 'text-foreground/70 hover:text-foreground hover:bg-surface-hover'
              }`}
            >
              <item.icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-foreground/60 group-hover:text-foreground'}`} />
              <span className="font-medium text-sm">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* User Footer Profile */}
      {user && (
        <div className="p-4 border-t border-border bg-surface-hover/50">
          <div className="flex items-center gap-3 mb-4 px-2">
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-secondary/30 to-primary/30 flex items-center justify-center border border-border">
              <UserIcon className="w-5 h-5 text-foreground/70" />
            </div>
            <div className="flex-1 overflow-hidden">
              <span className="font-medium text-sm block truncate text-foreground">{user.name}</span>
              <span className="text-xs block text-foreground/50 truncate">{user.email}</span>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl border border-border hover:bg-red-500/10 hover:text-red-500 text-foreground/70 text-sm font-medium transition-all"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out</span>
          </button>
        </div>
      )}
    </aside>
  );
}
