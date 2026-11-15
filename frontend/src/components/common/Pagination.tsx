import React from 'react';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';

export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  limit?: number;
  pageSize?: number;
  totalItems: number;
  onPageChange: (page: number) => void;
  onLimitChange?: (limit: number) => void;
  onPageSizeChange?: (pageSize: number) => void;
  pageSizeOptions?: number[];
  limitOptions?: number[];
}

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  limit,
  pageSize,
  totalItems,
  onPageChange,
  onLimitChange,
  onPageSizeChange,
  pageSizeOptions,
  limitOptions,
}) => {
  if (totalItems === 0) return null;

  const currentLimit = limit ?? pageSize ?? 10;
  const options = limitOptions ?? pageSizeOptions ?? [5, 10, 20, 50];
  const changeHandler = onLimitChange ?? onPageSizeChange;

  const startItem = (currentPage - 1) * currentLimit + 1;
  const endItem = Math.min(currentPage * currentLimit, totalItems);

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-3 px-6 py-3.5 bg-white border-t border-slate-200 text-xs text-slate-600">
      {/* Left: Summary and Limit */}
      <div className="flex items-center gap-3">
        <span>
          Showing <strong className="font-semibold text-slate-800">{startItem}</strong> to{' '}
          <strong className="font-semibold text-slate-800">{endItem}</strong> of{' '}
          <strong className="font-semibold text-slate-800">{totalItems}</strong> entries
        </span>

        {changeHandler && (
          <div className="hidden sm:flex items-center gap-1.5 ml-2">
            <span className="text-slate-400">Rows:</span>
            <select
              value={currentLimit}
              onChange={(e) => {
                changeHandler(Number(e.target.value));
                onPageChange(1);
              }}
              className="bg-slate-50 border border-slate-200 text-slate-700 text-xs rounded px-1.5 py-0.5 focus:outline-none focus:border-slate-400 cursor-pointer"
            >
              {options.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Right: Page Navigation Controls */}
      <div className="flex items-center gap-1">
        <button
          type="button"
          onClick={() => onPageChange(1)}
          disabled={currentPage <= 1}
          className="p-1.5 rounded border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
          title="First Page"
        >
          <ChevronsLeft className="w-3.5 h-3.5" />
        </button>

        <button
          type="button"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage <= 1}
          className="p-1.5 rounded border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
          title="Previous Page"
        >
          <ChevronLeft className="w-3.5 h-3.5" />
        </button>

        <span className="px-3 py-1 text-xs font-medium text-slate-700">
          Page <strong className="text-slate-900 font-semibold">{currentPage}</strong> of{' '}
          <strong className="text-slate-900 font-semibold">{Math.max(1, totalPages)}</strong>
        </span>

        <button
          type="button"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages}
          className="p-1.5 rounded border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
          title="Next Page"
        >
          <ChevronRight className="w-3.5 h-3.5" />
        </button>

        <button
          type="button"
          onClick={() => onPageChange(totalPages)}
          disabled={currentPage >= totalPages}
          className="p-1.5 rounded border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
          title="Last Page"
        >
          <ChevronsRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
