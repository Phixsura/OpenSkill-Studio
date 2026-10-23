"use client";

interface PaginationMeta { page: number; per_page: number; total: number; total_pages: number; has_next: boolean; has_prev: boolean; }
interface PaginationControlsProps { meta: PaginationMeta; onPageChange: (page: number) => void; }

export function PaginationControls({ meta, onPageChange }: PaginationControlsProps) {
  const pages = Array.from({ length: Math.min(meta.total_pages, 7) }, (_, i) => {
    if (meta.total_pages <= 7) return i + 1;
    if (i === 0) return 1;
    if (i === 6) return meta.total_pages;
    return Math.max(2, Math.min(meta.total_pages - 1, meta.page - 2 + i));
  });

  return (
    <div className="flex items-center justify-between">
      <p className="text-xs text-gray-400">
        {(meta.page - 1) * meta.per_page + 1}–{Math.min(meta.page * meta.per_page, meta.total)} of {meta.total}
      </p>
      <div className="flex gap-1">
        <button onClick={() => onPageChange(meta.page - 1)} disabled={!meta.has_prev}
          className="rounded border px-2 py-1 text-xs disabled:opacity-30 dark:border-gray-600">←</button>
        {pages.map(p => (
          <button key={p} onClick={() => onPageChange(p)}
            className={`rounded px-2.5 py-1 text-xs ${p === meta.page ? "bg-blue-600 text-white" : "border dark:border-gray-600"}`}>
            {p}
          </button>
        ))}
        <button onClick={() => onPageChange(meta.page + 1)} disabled={!meta.has_next}
          className="rounded border px-2 py-1 text-xs disabled:opacity-30 dark:border-gray-600">→</button>
      </div>
    </div>
  );
}
