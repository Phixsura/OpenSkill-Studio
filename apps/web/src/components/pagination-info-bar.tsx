"use client";

interface PaginationInfoBarProps { display: string; page: number; totalPages: number;
  pages: number[]; hasPrev: boolean; hasNext: boolean;
  onPageChange: (page: number) => void; }

export function PaginationInfoBar({ display, page, totalPages, pages, hasPrev, hasNext, onPageChange }: PaginationInfoBarProps) {
  return (
    <div className="flex items-center justify-between">
      <p className="text-xs text-gray-400">{display}</p>
      {totalPages > 1 && (
        <div className="flex items-center gap-1">
          <button onClick={() => onPageChange(page - 1)} disabled={!hasPrev}
            className="rounded border px-2 py-1 text-xs disabled:opacity-30 dark:border-gray-600">←</button>
          {pages.map(p => (
            <button key={p} onClick={() => onPageChange(p)}
              className={`rounded px-2.5 py-1 text-xs ${p === page ? "bg-blue-600 text-white" : "border dark:border-gray-600"}`}>
              {p}
            </button>
          ))}
          <button onClick={() => onPageChange(page + 1)} disabled={!hasNext}
            className="rounded border px-2 py-1 text-xs disabled:opacity-30 dark:border-gray-600">→</button>
        </div>
      )}
    </div>
  );
}
