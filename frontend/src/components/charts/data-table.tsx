'use client';

import { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface DataTableProps {
  data: Record<string, any>[];
  pageSize?: number;
}

export default function DataTableComponent({
  data,
  pageSize = 10,
}: DataTableProps) {
  const [currentPage, setCurrentPage] = useState(1);

  if (!data || data.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-sm text-foreground/50">
        No records available
      </div>
    );
  }

  // Get columns from the first object
  const columns = Object.keys(data[0]);
  
  // Pagination
  const totalPages = Math.ceil(data.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const paginatedData = data.slice(startIndex, startIndex + pageSize);

  return (
    <div className="flex flex-col h-full justify-between">
      {/* Table container */}
      <div className="overflow-auto border border-border rounded-xl flex-1 max-h-[400px]">
        <table className="w-full text-sm border-collapse text-left">
          <thead className="sticky top-0 bg-surface border-b border-border text-foreground/75 font-semibold text-xs tracking-wider uppercase z-[1]">
            <tr>
              {columns.map((col) => (
                <th key={col} className="p-3.5 whitespace-nowrap bg-surface-hover/80">
                  {col.replace('_', ' ').toUpperCase()}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border/60">
            {paginatedData.map((row, idx) => (
              <tr key={idx} className="hover:bg-surface-hover/30 transition-colors">
                {columns.map((col) => {
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

      {/* Pagination controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-border mt-3 pt-3 px-2">
          <span className="text-xs text-foreground/50">
            Showing <strong className="text-foreground/70">{startIndex + 1}</strong> to{' '}
            <strong className="text-foreground/70">{Math.min(startIndex + pageSize, data.length)}</strong> of{' '}
            <strong className="text-foreground/70">{data.length}</strong> entries
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
              disabled={currentPage === 1}
              className="p-1.5 rounded-lg border border-border bg-surface text-foreground/60 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-surface-hover hover:text-foreground transition-all"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="text-xs self-center font-semibold text-foreground/70">
              {currentPage} / {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="p-1.5 rounded-lg border border-border bg-surface text-foreground/60 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-surface-hover hover:text-foreground transition-all"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
