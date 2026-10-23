"use client";

interface PaginationControlsProps { page: number; totalPages: number; onPageChange: (p: number) => void; }

export function PaginationControls({ page, totalPages, onPageChange }: PaginationControlsProps) {
  if (totalPages <= 1) return null;
  const pages = Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
    if (totalPages <= 7) return i + 1;
    if (i === 0) return 1;
    if (i === 6) return totalPages;
    return Math.max(2, Math.min(totalPages - 1, page - 2 + i));
  });

  return (
    <div className="flex items-center justify-center gap-1">
      <button onClick={() => onPageChange(page - 1)} disabled={page <= 1}
        className="rounded border px-3 py-1 text-sm disabled:opacity-30">←</button>
      {pages.map(p => (
        <button key={p} onClick={() => onPageChange(p)}
          className={`rounded px-3 py-1 text-sm ${p === page ? "bg-blue-600 text-white" : "border hover:bg-gray-50 dark:border-gray-700"}`}>{p}</button>
      ))}
      <button onClick={() => onPageChange(page + 1)} disabled={page >= totalPages}
        className="rounded border px-3 py-1 text-sm disabled:opacity-30">→</button>
    </div>
  );
}
