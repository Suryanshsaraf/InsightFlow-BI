'use client';

import { useEffect, useState } from 'react';
import { useDashboardStore } from '@/stores/dashboard-store';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  LayoutDashboard, 
  Trash2, 
  ArrowRight, 
  Loader2, 
  Calendar,
  Layers,
  Database
} from 'lucide-react';

export default function DashboardsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const datasetId = searchParams.get('datasetId');
  
  const { 
    dashboards, 
    isLoading, 
    fetchDashboards, 
    deleteDashboard 
  } = useDashboardStore();

  const [deleteId, setDeleteId] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboards();
  }, [fetchDashboards]);

  // Handle auto-redirect if datasetId is present
  useEffect(() => {
    if (datasetId && dashboards.length > 0) {
      // Find dashboard for this dataset
      const matched = dashboards.find((d) => d.datasetId === datasetId);
      if (matched) {
        router.push(`/dashboards/${matched.id}`);
      }
    }
  }, [datasetId, dashboards, router]);

  const handleDelete = async (id: string) => {
    setDeleteId(id);
    try {
      await deleteDashboard(id);
    } catch {
      // handled by store
    } finally {
      setDeleteId(null);
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight text-foreground">Interactive Dashboards</h2>
        <p className="text-foreground/50 font-medium">
          View auto-generated visualizations, compile KPI metrics, and explore business intelligence insights.
        </p>
      </div>

      {isLoading && dashboards.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 gap-3 glass-panel rounded-2xl border border-border">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
          <span className="text-sm font-semibold text-foreground/50">Fetching dashboards...</span>
        </div>
      ) : dashboards.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 px-8 text-center glass-panel rounded-2xl border border-border gap-5">
          <LayoutDashboard className="w-12 h-12 text-foreground/20" />
          <div>
            <h4 className="font-bold text-base text-foreground">No dashboards found</h4>
            <p className="text-foreground/50 text-sm mt-1 max-w-sm">
              Please go to the <Link href="/datasets" className="text-primary font-bold hover:underline">Datasets</Link> tab, upload a CSV file, and wait for analytics to generate.
            </p>
          </div>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {dashboards.map((dashboard) => (
            <div 
              key={dashboard.id}
              className="glass-panel p-6 rounded-2xl border border-border flex flex-col justify-between hover:border-primary/30 transition-all duration-300 group"
            >
              <div>
                {/* Title */}
                <h4 className="font-bold text-lg text-foreground group-hover:text-primary transition-colors truncate mb-2">
                  {dashboard.name}
                </h4>
                {/* Description */}
                <p className="text-sm text-foreground/50 line-clamp-2 mb-6 font-medium">
                  {dashboard.description || 'No description provided.'}
                </p>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-border/40 gap-4 mt-auto">
                <span className="text-[10px] font-bold text-foreground/45 flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5" />
                  <span>{new Date(dashboard.createdAt).toLocaleDateString()}</span>
                </span>

                <div className="flex gap-2">
                  <button
                    onClick={() => handleDelete(dashboard.id)}
                    disabled={deleteId === dashboard.id}
                    className="p-2 rounded-lg border border-border text-foreground/50 hover:text-red-500 hover:bg-red-500/5 transition-colors disabled:opacity-40"
                  >
                    {deleteId === dashboard.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                  </button>
                  <Link
                    href={`/dashboards/${dashboard.id}`}
                    className="px-4 py-2 rounded-lg bg-primary hover:bg-primary-hover text-white font-bold text-xs flex items-center gap-1.5 transition-all shadow-md shadow-primary/10"
                  >
                    <span>View Report</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
