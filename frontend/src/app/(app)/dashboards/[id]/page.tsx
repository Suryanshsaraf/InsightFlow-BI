'use client';

import { useEffect, useState, use } from 'react';
import { useDashboardStore } from '@/stores/dashboard-store';
import { useDatasetStore } from '@/stores/dataset-store';
import apiClient from '@/lib/api-client';
import ChartRenderer from '@/components/charts/chart-renderer';
import { Responsive } from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import { 
  Sparkles, 
  RefreshCw, 
  TrendingUp, 
  TrendingDown, 
  AlertOctagon, 
  BrainCircuit, 
  FileText, 
  Loader2,
  Filter,
  X,
  Plus
} from 'lucide-react';
import { useRef } from 'react';

export default function DashboardViewPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const dashboardId = resolvedParams.id;

  const { 
    activeDashboard, 
    isLoading, 
    fetchDashboardDetails, 
    updateDashboardLayout 
  } = useDashboardStore();

  const { fetchDatasetDetails, activeDataset } = useDatasetStore();
  
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState(1200);

  useEffect(() => {
    if (!containerRef.current) return;
    const handleResize = () => {
      if (containerRef.current) {
        setContainerWidth(containerRef.current.offsetWidth);
      }
    };
    handleResize();
    const observer = new ResizeObserver(handleResize);
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, [activeDashboard]);

  const [insights, setInsights] = useState<any[]>([]);
  const [executiveSummary, setExecutiveSummary] = useState<string>('');
  const [isGeneratingInsights, setIsGeneratingInsights] = useState(false);
  
  // Interactive filters
  const [selectedFilters, setSelectedFilters] = useState<Record<string, string>>({});
  const [chartDataOverrides, setChartDataOverrides] = useState<Record<string, any[]>>({});
  const [isFilteringCharts, setIsFilteringCharts] = useState<Record<string, boolean>>({});

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const dashboardData = await fetchDashboardDetails(dashboardId);
        if (dashboardData.datasetId) {
          await fetchDatasetDetails(dashboardData.datasetId);
        }
        // Load insights
        loadInsights();
      } catch (err) {
        console.error(err);
      }
    };
    loadDashboard();
  }, [dashboardId, fetchDashboardDetails, fetchDatasetDetails]);

  // Load insights
  const loadInsights = async () => {
    try {
      const { data } = await apiClient.get(`/insights/dashboard/${dashboardId}`);
      if (Array.isArray(data)) {
        setInsights(data);
        // Find a summary type for executive summary or set first
        const summary = data.find((ins) => ins.type === 'summary');
        setExecutiveSummary(summary ? summary.description : 'Executive summary of your dataset compiled.');
      } else {
        setExecutiveSummary(data.executive_summary || '');
        setInsights(data.insights || []);
      }
    } catch (err) {
      console.error('Failed to load insights', err);
    }
  };

  // Trigger insight generation
  const handleGenerateInsights = async () => {
    setIsGeneratingInsights(true);
    try {
      const { data } = await apiClient.post('/insights/generate', { dashboardId });
      if (Array.isArray(data)) {
        setInsights(data);
        const summary = data.find((ins) => ins.type === 'summary');
        setExecutiveSummary(summary ? summary.description : '');
      } else {
        setExecutiveSummary(data.executive_summary || '');
        setInsights(data.insights || []);
      }
    } catch (err) {
      console.error('Failed to generate insights', err);
    } finally {
      setIsGeneratingInsights(false);
    }
  };

  // Layout save
  const handleLayoutChange = (currentLayout: readonly any[]) => {
    if (activeDashboard) {
      const mappedLayout = currentLayout.map((item) => ({
        i: item.i,
        x: item.x,
        y: item.y,
        w: item.w,
        h: item.h,
      }));
      updateDashboardLayout(dashboardId, mappedLayout);
    }
  };

  // Apply interactive filters
  const handleFilterChange = async (column: string, value: string) => {
    const updatedFilters = { ...selectedFilters };
    if (value === '') {
      delete updatedFilters[column];
    } else {
      updatedFilters[column] = value;
    }
    setSelectedFilters(updatedFilters);
    
    // Map filters to backend shape
    const backendFilters = Object.entries(updatedFilters).map(([col, val]) => ({
      column: col,
      operator: 'eq',
      value: val,
    }));

    if (!activeDashboard) return;

    // Reload each chart with filters applied
    for (const chart of activeDashboard.charts) {
      const chartId = chart.id;
      setIsFilteringCharts(prev => ({ ...prev, [chartId]: true }));
      try {
        const { data } = await apiClient.post(`/charts/${chartId}/data`, {
          filters: backendFilters,
        });
        setChartDataOverrides(prev => ({ ...prev, [chartId]: data.rows }));
      } catch (err) {
        console.error(`Failed to fetch filtered data for chart ${chartId}`, err);
      } finally {
        setIsFilteringCharts(prev => ({ ...prev, [chartId]: false }));
      }
    }
  };

  const clearAllFilters = () => {
    setSelectedFilters({});
    setChartDataOverrides({});
  };

  if (isLoading || !activeDashboard) {
    return (
      <div className="flex flex-col items-center justify-center py-40 gap-3">
        <Loader2 className="w-10 h-10 text-primary animate-spin" />
        <span className="text-sm font-semibold text-foreground/50">Loading dashboard report...</span>
      </div>
    );
  }

  // Get list of categorical columns for filters
  const filterColumns = activeDataset?.columns?.filter((col) => col.type === 'string') || [];

  return (
    <div className="space-y-8 pb-12">
      
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-extrabold text-foreground tracking-tight">{activeDashboard.name}</h2>
          <p className="text-sm text-foreground/50 font-medium mt-1">{activeDashboard.description}</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleGenerateInsights}
            disabled={isGeneratingInsights}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-primary to-secondary text-white hover:opacity-95 font-semibold text-sm transition-all shadow-lg shadow-primary/10 flex items-center gap-2 cursor-pointer disabled:opacity-40"
          >
            {isGeneratingInsights ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Sparkles className="w-4 h-4" />
            )}
            <span>Regenerate Insights</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Row */}
      {activeDashboard.kpis && activeDashboard.kpis.length > 0 && (
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {activeDashboard.kpis.map((kpi: any) => {
            const isUp = kpi.trend === 'up';
            const isDown = kpi.trend === 'down';
            
            // Format number
            let formattedValue = kpi.value;
            if (typeof kpi.value === 'number') {
              if (kpi.format === 'currency') {
                formattedValue = kpi.value.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
              } else if (kpi.format === 'percentage') {
                formattedValue = `${kpi.value.toFixed(1)}%`;
              } else {
                formattedValue = kpi.value.toLocaleString();
              }
            }

            return (
              <div key={kpi.id} className="glass-panel p-6 rounded-2xl border border-border flex flex-col justify-between">
                <div>
                  <span className="text-xs font-bold text-foreground/45 uppercase tracking-wider block mb-1">
                    {kpi.title}
                  </span>
                  <span className="text-2xl font-extrabold text-foreground tracking-tight">
                    {formattedValue}
                  </span>
                </div>
                {kpi.trendValue !== null && kpi.trendValue !== undefined && (
                  <div className="flex items-center gap-1.5 mt-4">
                    {isUp && (
                      <span className="flex items-center gap-1 text-xs font-extrabold text-green-500 bg-green-500/10 px-2 py-0.5 rounded-full border border-green-500/10">
                        <TrendingUp className="w-3 h-3" />
                        <span>+{kpi.trendValue}%</span>
                      </span>
                    )}
                    {isDown && (
                      <span className="flex items-center gap-1 text-xs font-extrabold text-red-500 bg-red-500/10 px-2 py-0.5 rounded-full border border-red-500/10">
                        <TrendingDown className="w-3 h-3" />
                        <span>{kpi.trendValue}%</span>
                      </span>
                    )}
                    <span className="text-[10px] font-bold text-foreground/40">vs previous period</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Main Layout Grid (Dashboard + AI Sidebar) */}
      <div className="grid lg:grid-cols-4 gap-8">
        
        {/* Left 3 Columns: Grid of Charts */}
        <div className="lg:col-span-3 space-y-6">
          
          {/* Interactive Filters Panel */}
          {filterColumns.length > 0 && (
            <div className="glass-panel p-4 rounded-2xl border border-border/80 flex flex-wrap items-center gap-4">
              <div className="flex items-center gap-2 text-foreground/60 font-semibold text-sm pr-2 border-r border-border/60">
                <Filter className="w-4 h-4 text-primary" />
                <span>Filters</span>
              </div>
              
              {filterColumns.map((col) => {
                const sampleValues = col.sampleValues || [];
                return (
                  <div key={col.name} className="flex flex-col gap-1">
                    <select
                      value={selectedFilters[col.name] || ''}
                      onChange={(e) => handleFilterChange(col.name, e.target.value)}
                      className="bg-surface border border-border/80 rounded-xl px-3 py-1.5 text-xs outline-none transition-all focus:border-primary font-semibold text-foreground/80 cursor-pointer"
                    >
                      <option value="">All {col.name.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}</option>
                      {sampleValues.map((val: any) => (
                        <option key={val} value={String(val)}>
                          {String(val)}
                        </option>
                      ))}
                    </select>
                  </div>
                );
              })}

              {Object.keys(selectedFilters).length > 0 && (
                <button
                  onClick={clearAllFilters}
                  className="text-xs font-bold text-red-500 hover:text-red-600 transition-colors flex items-center gap-1 ml-auto"
                >
                  <X className="w-3.5 h-3.5" />
                  <span>Reset Filters</span>
                </button>
              )}
            </div>
          )}

          {/* Draggable grid */}
          {activeDashboard.layout && activeDashboard.layout.length > 0 ? (
            <div ref={containerRef} className="w-full">
              <Responsive
                className="layout"
                layouts={{ lg: activeDashboard.layout.map((item) => ({ ...item, minW: 3, minH: 3 })) }}
                breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
                cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
                rowHeight={100}
                width={containerWidth}
                onLayoutChange={handleLayoutChange}
                margin={[20, 20]}
              >
                {activeDashboard.charts.map((chart) => {
                  const chartId = chart.id;
                  const rows = chartDataOverrides[chartId] || chart.data || [];
                  const isFiltering = isFilteringCharts[chartId];

                  return (
                    <div
                      key={chartId}
                      className="glass-panel rounded-2xl border border-border/90 flex flex-col p-4 justify-between bg-surface relative group overflow-hidden"
                    >
                      {/* Handle and Title */}
                      <div className="flex items-center justify-between mb-4 border-b border-border/40 pb-2 drag-handle cursor-move">
                        <div>
                          <h4 className="font-extrabold text-sm text-foreground/80 tracking-tight leading-none">
                            {chart.chartConfig.title}
                          </h4>
                          <span className="text-[10px] text-foreground/45 font-medium mt-1 block">
                            {chart.chartConfig.description}
                          </span>
                        </div>
                        {/* Drag dot indicators */}
                        <div className="flex flex-col gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                          <span className="w-1.5 h-1.5 rounded-full bg-foreground/30" />
                          <span className="w-1.5 h-1.5 rounded-full bg-foreground/30" />
                          <span className="w-1.5 h-1.5 rounded-full bg-foreground/30" />
                        </div>
                      </div>

                      {/* Chart visual content */}
                      <div className="flex-1 flex items-center justify-center min-h-0 relative">
                        {isFiltering && (
                          <div className="absolute inset-0 bg-surface/60 backdrop-blur-[2px] z-[2] flex items-center justify-center rounded-xl">
                            <Loader2 className="w-6 h-6 text-primary animate-spin" />
                          </div>
                        )}
                        <ChartRenderer
                          type={chart.chartConfig.type as any}
                          data={rows}
                          xField={chart.chartConfig.xAxis?.field}
                          yField={chart.chartConfig.yAxis?.field}
                          colors={chart.chartConfig.colorScheme}
                          showGrid={chart.chartConfig.showGrid}
                        />
                      </div>
                    </div>
                  );
                })}
              </Responsive>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-20 gap-3 glass-panel rounded-2xl border border-border">
              <Loader2 className="w-8 h-8 text-primary animate-spin" />
              <span className="text-sm font-semibold text-foreground/50">Compiling report grids...</span>
            </div>
          )}
        </div>

        {/* Right 1 Column: AI Insights Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          <div className="glass-panel p-6 rounded-2xl border border-border/90 bg-surface flex flex-col h-fit sticky top-24">
            
            {/* Header */}
            <div className="flex items-center gap-2.5 pb-4 border-b border-border/40 mb-5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-secondary/20 to-primary/20 flex items-center justify-center border border-border">
                <BrainCircuit className="w-4 h-4 text-secondary" />
              </div>
              <div>
                <h3 className="font-extrabold text-sm text-foreground">AI Intelligence</h3>
                <span className="text-[10px] text-foreground/45 font-bold uppercase tracking-wider block">Insight Engine</span>
              </div>
            </div>

            {/* Executive Summary */}
            {executiveSummary && (
              <div className="p-4 rounded-xl bg-primary/5 border border-primary/10 mb-6 text-xs text-foreground/75 leading-relaxed font-semibold">
                <p>{executiveSummary}</p>
              </div>
            )}

            {/* Insights Cards List */}
            <div className="space-y-4 max-h-[500px] overflow-y-auto pr-1">
              {insights.filter(ins => ins.type !== 'summary').map((insight, idx) => {
                const isAnomaly = insight.type === 'anomaly';
                const isRecommendation = insight.type === 'recommendation';
                const isTrend = insight.type === 'trend';
                
                return (
                  <div 
                    key={insight.id || idx} 
                    className={`p-4 rounded-xl border text-xs flex flex-col justify-between hover:scale-[1.01] transition-transform ${
                      isAnomaly 
                        ? 'bg-red-500/5 border-red-500/10' 
                        : isRecommendation 
                          ? 'bg-purple-500/5 border-purple-500/10'
                          : isTrend
                            ? 'bg-green-500/5 border-green-500/10'
                            : 'bg-surface-hover/30 border-border/50'
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <span className={`font-extrabold uppercase tracking-wider text-[9px] px-1.5 py-0.5 rounded-md border ${
                          isAnomaly 
                            ? 'bg-red-500/10 text-red-500 border-red-500/10' 
                            : isRecommendation 
                              ? 'bg-purple-500/10 text-purple-500 border-purple-500/10'
                              : isTrend
                                ? 'bg-green-500/10 text-green-500 border-green-500/10'
                                : 'bg-foreground/5 text-foreground/60 border-border'
                        }`}>
                          {insight.type}
                        </span>
                        {insight.confidence !== undefined && (
                          <span className="text-[9px] font-bold text-foreground/40">
                            Confidence: {Math.round(insight.confidence * 100)}%
                          </span>
                        )}
                      </div>
                      <h4 className="font-extrabold text-foreground/80 mb-1 leading-snug">{insight.title}</h4>
                      <p className="text-foreground/50 leading-relaxed font-semibold">{insight.description}</p>
                    </div>
                  </div>
                );
              })}

              {insights.length === 0 && (
                <div className="text-center py-8 text-xs text-foreground/45 font-semibold">
                  No automated insights compiled. Click "Regenerate Insights" above to trigger.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
