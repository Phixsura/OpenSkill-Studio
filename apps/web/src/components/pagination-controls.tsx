"use client";

interface PaginationControlsProps {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export function PaginationControls({ page, totalPages, onPageChange }: PaginationControlsProps) {
  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-center gap-2 py-4">
      <button onClick={() => onPageChange(page - 1)} disabled={page <= 1}
        className="rounded border px-3 py-1 text-sm disabled:opacity-30">← Prev</button>
      <span className="text-sm text-gray-600 dark:text-gray-400">
        Page {page} of {totalPages}
      </span>
      <button onClick={() => onPageChange(page + 1)} disabled={page >= totalPages}
        className="rounded border px-3 py-1 text-sm disabled:opacity-30">Next →</button>
    </div>
  );
}
