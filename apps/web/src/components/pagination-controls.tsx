"use client";

interface PaginationControlsProps { page: number; totalPages: number;
  pages: number[]; showing: string; hasPrev: boolean; hasNext: boolean;
  onPage: (page: number) => void; }

export function PaginationControls({ page, totalPages, pages, showing, hasPrev, hasNext, onPage }: PaginationControlsProps) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-xs text-gray-400">{showing}</span>
      <div className="flex gap-1">
        <button onClick={() => onPage(page - 1)} disabled={!hasPrev}
          className="px-2 py-1 rounded border text-xs disabled:opacity-30 hover:bg-gray-50 dark:hover:bg-gray-800">←</button>
        {pages.map(p => (
          <button key={p} onClick={() => onPage(p)}
            className={`px-2.5 py-1 rounded text-xs ${p === page ? "bg-blue-600 text-white" : "border hover:bg-gray-50 dark:hover:bg-gray-800"}`}>{p}</button>
        ))}
        <button onClick={() => onPage(page + 1)} disabled={!hasNext}
          className="px-2 py-1 rounded border text-xs disabled:opacity-30 hover:bg-gray-50 dark:hover:bg-gray-800">→</button>
      </div>
    </div>
  );
}
