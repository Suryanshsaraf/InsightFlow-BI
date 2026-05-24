'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { useDatasetStore } from '@/stores/dataset-store';
import apiClient from '@/lib/api-client';
import { 
  Code2, 
  Sparkles, 
  Play, 
  History, 
  Database, 
  Loader2, 
  AlertTriangle,
  Terminal,
  FileSpreadsheet,
  Clock,
  CheckCircle2,
  XCircle
} from 'lucide-react';

// Dynamically import CodeMirror to prevent SSR hydration issues
const CodeMirror = dynamic(
  () => import('@uiw/react-codemirror').then((mod) => mod.default),
  { ssr: false }
);

export default function QueryPage() {
  const { datasets, isLoading: isDatasetsLoading, fetchDatasets } = useDatasetStore();
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>('');
  
  // Query state
  const [sqlQuery, setSqlQuery] = useState<string>('');
  const [nlQuestion, setNlQuestion] = useState<string>('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Results state
  const [results, setResults] = useState<any[]>([]);
  const [resultsColumns, setResultsColumns] = useState<string[]>([]);
  const [executionTime, setExecutionTime] = useState<number>(0);
  const [rowCount, setRowCount] = useState<number>(0);

  // History state
  const [history, setHistory] = useState<any[]>([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);

  // Load datasets on mount
  useEffect(() => {
    fetchDatasets();
  }, [fetchDatasets]);

  // Set initial selected dataset
  useEffect(() => {
    if (datasets.length > 0 && !selectedDatasetId) {
      const firstReady = datasets.find((d) => d.status === 'ready');
      if (firstReady) {
        setSelectedDatasetId(firstReady.id);
        const name = firstReady.name;
        // Set basic boilerplate query
        setSqlQuery(`SELECT * FROM ${firstReady.id} LIMIT 10;`);
      }
    }
  }, [datasets, selectedDatasetId]);

  // Fetch history when dataset selection changes
  useEffect(() => {
    if (selectedDatasetId) {
      fetchQueryHistory(selectedDatasetId);
      // Update boilerplate SQL
      const selected = datasets.find(d => d.id === selectedDatasetId);
      if (selected) {
        // Table name placeholder can be anything, our backend will rewrite it to the user's isolated table.
        // We use the actual ID or dataset name, the query engine will rewrite it correctly.
        setSqlQuery(`SELECT * FROM ${selected.id} LIMIT 10;`);
      }
    }
  }, [selectedDatasetId, datasets]);

  const fetchQueryHistory = async (dsId: string) => {
    setIsHistoryLoading(true);
    try {
      const { data } = await apiClient.get('/queries/history', {
        params: { datasetId: dsId }
      });
      setHistory(data);
    } catch (err) {
      console.error('Failed to fetch history', err);
    } finally {
      setIsHistoryLoading(false);
    }
  };

  const handleExecute = async () => {
    if (!selectedDatasetId || !sqlQuery.trim()) return;
    
    setIsExecuting(true);
    setError(null);
    setResults([]);
    setResultsColumns([]);

    try {
      const { data } = await apiClient.post('/queries/execute', {
        datasetId: selectedDatasetId,
        sqlQuery: sqlQuery,
      });

      if (data.results && data.results.length > 0) {
        setResults(data.results);
        setResultsColumns(Object.keys(data.results[0]));
        setRowCount(data.results.length);
      } else {
        setResults([]);
        setResultsColumns([]);
        setRowCount(0);
      }
      setExecutionTime(data.executionTimeMs || 0.0);
      
      // Refresh history
      fetchQueryHistory(selectedDatasetId);
    } catch (err: any) {
      setError(
        err.response?.data?.error?.message || 
        'Failed to execute SQL query. Please review syntax rules.'
      );
      fetchQueryHistory(selectedDatasetId);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleTranslate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDatasetId || !nlQuestion.trim()) return;

    setIsTranslating(true);
    setError(null);

    try {
      const { data } = await apiClient.post('/queries/natural-language', {
        datasetId: selectedDatasetId,
        question: nlQuestion,
      });

      // Update SQL Editor with generated query
      setSqlQuery(data.sqlQuery);
      
      // Load results immediately
      if (data.results && data.results.length > 0) {
        setResults(data.results);
        setResultsColumns(Object.keys(data.results[0]));
        setRowCount(data.results.length);
      } else {
        setResults([]);
        setResultsColumns([]);
        setRowCount(0);
      }
      setExecutionTime(data.executionTimeMs || 0.0);
      
      // Reset question input
      setNlQuestion('');
      
      // Refresh history
      fetchQueryHistory(selectedDatasetId);
    } catch (err: any) {
      setError(
        err.response?.data?.error?.message || 
        'AI Translation failed. Please try a simpler question.'
      );
    } finally {
      setIsTranslating(false);
    }
  };

  const handleLoadHistoryItem = (item: any) => {
    if (item.sqlQuery) {
      setSqlQuery(item.sqlQuery);
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-foreground">Query Workbench</h2>
          <p className="text-foreground/50 font-medium">
            Run raw SQL SELECT queries on your isolated schemas or use plain English to let the AI build queries.
          </p>
        </div>

        {/* Dataset Selection */}
        <div className="flex items-center gap-3">
          <Database className="w-5 h-5 text-foreground/40" />
          <select
            value={selectedDatasetId}
            onChange={(e) => setSelectedDatasetId(e.target.value)}
            className="bg-surface border border-border/80 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-primary font-bold text-foreground/80 cursor-pointer"
          >
            {datasets.filter(d => d.status === 'ready').map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
            {datasets.length === 0 && <option value="">No Active Datasets</option>}
          </select>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid lg:grid-cols-4 gap-8">
        
        {/* Left 3 Columns: NL prompt + SQL Editor + Results Table */}
        <div className="lg:col-span-3 space-y-6">
          
          {/* NL Input Section */}
          <div className="glass-panel p-5 rounded-2xl border border-border">
            <h3 className="font-extrabold text-sm text-foreground mb-3 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-secondary" />
              <span>Ask in Plain English</span>
            </h3>

            <form onSubmit={handleTranslate} className="flex gap-3">
              <input
                type="text"
                value={nlQuestion}
                onChange={(e) => setNlQuestion(e.target.value)}
                placeholder="e.g. What are the top 5 records by revenue? or How many transactions happened in March?"
                className="flex-1 bg-surface border border-border/80 focus:border-primary rounded-xl py-3 px-4 text-sm outline-none transition-all placeholder:text-foreground/30 font-medium"
              />
              <button
                type="submit"
                disabled={isTranslating || !selectedDatasetId || !nlQuestion.trim()}
                className="px-5 py-3 rounded-xl bg-gradient-to-r from-primary to-secondary text-white hover:opacity-95 disabled:opacity-40 font-semibold text-sm transition-all shadow-lg shadow-primary/20 flex items-center gap-2 cursor-pointer"
              >
                {isTranslating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Translating...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Ask AI</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* SQL Editor Section */}
          <div className="glass-panel rounded-2xl border border-border overflow-hidden">
            <div className="h-12 bg-surface-hover/80 px-6 border-b border-border flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold text-foreground/60 uppercase tracking-wider">
                <Terminal className="w-4 h-4 text-primary" />
                <span>SQL Workbench</span>
              </div>

              <button
                onClick={handleExecute}
                disabled={isExecuting || !sqlQuery.trim() || !selectedDatasetId}
                className="px-4 py-1.5 rounded-lg bg-primary hover:bg-primary-hover disabled:bg-primary/40 text-white font-bold text-xs transition-all shadow-md shadow-primary/10 flex items-center gap-1.5 cursor-pointer"
              >
                {isExecuting ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Play className="w-3.5 h-3.5 fill-white" />
                )}
                <span>Run Query</span>
              </button>
            </div>

            {/* CodeMirror input */}
            <div className="border-b border-border">
              <CodeMirror
                value={sqlQuery}
                height="180px"
                theme="dark"
                onChange={(value) => setSqlQuery(value)}
                className="text-sm font-mono focus-within:outline-none"
              />
            </div>

            {/* Stats Footer bar */}
            {rowCount > 0 && (
              <div className="h-10 bg-surface/50 px-6 flex items-center gap-6 text-xs font-bold text-foreground/50">
                <span className="flex items-center gap-1">
                  <FileSpreadsheet className="w-4 h-4 text-foreground/30" />
                  Rows: {rowCount}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4 text-foreground/30" />
                  Time: {executionTime.toFixed(1)}ms
                </span>
              </div>
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 text-sm flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
              <div className="space-y-1">
                <span className="font-bold">Execution Failed</span>
                <p className="font-semibold text-xs leading-relaxed text-red-500/80">{error}</p>
              </div>
            </div>
          )}

          {/* Results Section */}
          <div className="glass-panel p-6 rounded-2xl border border-border">
            <h3 className="font-extrabold text-sm text-foreground mb-4 flex items-center gap-2">
              <FileSpreadsheet className="w-5 h-5 text-accent" />
              <span>Query Results</span>
            </h3>

            {isExecuting ? (
              <div className="flex flex-col items-center justify-center py-20 gap-3">
                <Loader2 className="w-8 h-8 text-primary animate-spin" />
                <span className="text-sm font-semibold text-foreground/50">Executing SQL query...</span>
              </div>
            ) : results.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 px-8 text-center border border-dashed border-border/80 rounded-xl gap-4">
                <Code2 className="w-10 h-10 text-foreground/20" />
                <span className="text-sm font-semibold text-foreground/40 max-w-xs">
                  Run a SQL statement or ask the AI a question to populate results here.
                </span>
              </div>
            ) : (
              <div className="overflow-x-auto border border-border rounded-xl">
                <table className="w-full text-sm border-collapse text-left">
                  <thead className="sticky top-0 bg-surface border-b border-border text-foreground/75 font-semibold text-xs tracking-wider uppercase">
                    <tr>
                      {resultsColumns.map((col) => (
                        <th key={col} className="p-3 whitespace-nowrap bg-surface-hover/80">
                          {col.replace('_', ' ').toUpperCase()}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/60">
                    {results.map((row, idx) => (
                      <tr key={idx} className="hover:bg-surface-hover/30 transition-colors">
                        {resultsColumns.map((col) => {
                          const val = row[col];
                          return (
                            <td key={col} className="p-3 text-foreground/80 font-medium truncate max-w-[200px]">
                              {val === null || val === undefined ? (
                                <span className="text-foreground/30 font-normal">null</span>
                              ) : typeof val === 'boolean' ? (
                                val ? 'True' : 'False'
                              ) : (
                                String(val)
                              )}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: History Sidebar */}
        <div className="lg:col-span-1 space-y-4">
          <h3 className="font-bold text-lg text-foreground flex items-center gap-2 px-1">
            <History className="w-5 h-5 text-foreground/60" />
            <span>Query History</span>
          </h3>

          <div className="glass-panel p-4 rounded-2xl border border-border space-y-3 h-[500px] overflow-y-auto bg-surface">
            {isHistoryLoading && history.length === 0 ? (
              <div className="flex justify-center py-10">
                <Loader2 className="w-6 h-6 text-primary animate-spin" />
              </div>
            ) : history.length === 0 ? (
              <div className="text-center py-10 text-xs text-foreground/40 font-semibold leading-relaxed">
                No past transactions recorded on this dataset.
              </div>
            ) : (
              history.map((item) => {
                const isSuccess = item.status === 'completed';
                return (
                  <div
                    key={item.id}
                    onClick={() => handleLoadHistoryItem(item)}
                    className="p-3 rounded-xl border border-border/80 bg-surface/30 hover:border-primary/40 hover:bg-surface-hover/20 cursor-pointer transition-all flex flex-col justify-between gap-2.5 group"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <span className="text-[10px] font-extrabold text-foreground/60 truncate flex-1 block">
                        {item.naturalLanguageQuery}
                      </span>
                      {isSuccess ? (
                        <CheckCircle2 className="w-3.5 h-3.5 text-green-500 shrink-0 mt-0.5" />
                      ) : (
                        <XCircle className="w-3.5 h-3.5 text-red-500 shrink-0 mt-0.5" />
                      )}
                    </div>

                    {/* SQL preview snippet */}
                    <code className="text-[9px] font-mono block bg-surface px-2 py-1 rounded text-foreground/75 truncate group-hover:text-primary transition-colors">
                      {item.sqlQuery}
                    </code>

                    <div className="flex items-center justify-between text-[9px] text-foreground/40 font-bold border-t border-border/40 pt-1.5">
                      <span>Rows: {item.rowCount}</span>
                      <span>Time: {item.executionTimeMs.toFixed(0)}ms</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
