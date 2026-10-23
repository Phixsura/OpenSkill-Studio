"use client";

interface PaginationControlsProps { page: number; totalPages: number; hasPrev: boolean;
  hasNext: boolean; onPageChange: (page: number) => void; }

export function PaginationControls({ page, totalPages, hasPrev, hasNext, onPageChange }: PaginationControlsProps) {
  const pages: number[] = [];
  const start = Math.max(1, page - 2);
  const end = Math.min(totalPages, page + 2);
  for (let i = start; i <= end; i++) pages.push(i);

  return (
    <div className="flex items-center justify-center gap-1">
      <button onClick={() => onPageChange(page - 1)} disabled={!hasPrev}
        className="rounded border px-2.5 py-1 text-sm disabled:opacity-30 dark:border-gray-700">←</button>
      {start > 1 && <><button onClick={() => onPageChange(1)} className="rounded px-2.5 py-1 text-sm hover:bg-gray-100 dark:hover:bg-gray-800">1</button><span className="text-gray-400">…</span></>}
      {pages.map(p => (
        <button key={p} onClick={() => onPageChange(p)}
          className={`rounded px-2.5 py-1 text-sm ${p === page ? "bg-blue-600 text-white" : "hover:bg-gray-100 dark:hover:bg-gray-800"}`}>{p}</button>
      ))}
      {end < totalPages && <><span className="text-gray-400">…</span><button onClick={() => onPageChange(totalPages)} className="rounded px-2.5 py-1 text-sm hover:bg-gray-100 dark:hover:bg-gray-800">{totalPages}</button></>}
      <button onClick={() => onPageChange(page + 1)} disabled={!hasNext}
        className="rounded border px-2.5 py-1 text-sm disabled:opacity-30 dark:border-gray-700">→</button>
    </div>
  );
}
