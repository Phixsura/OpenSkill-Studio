"use client";

interface Column { key: string; label: string; sortable: boolean; }
interface DataTableProps { columns: Column[]; rows: Record<string, unknown>[];
  total: number; page: number; totalPages: number;
  sortBy: string | null; sortDir: string;
  onSort: (key: string) => void; onPageChange: (page: number) => void; }

export function DataTable({ columns, rows, total, page, totalPages, sortBy, sortDir, onSort, onPageChange }: DataTableProps) {
  return (
    <div className="space-y-3">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="border-b dark:border-gray-700">
            {columns.map(col => (
              <th key={col.key} className="px-3 py-2 text-left font-medium">
                {col.sortable ? (
                  <button onClick={() => onSort(col.key)} className="flex items-center gap-1 hover:text-blue-600">
                    {col.label}{sortBy === col.key && <span>{sortDir === "asc" ? "↑" : "↓"}</span>}
                  </button>
                ) : col.label}
              </th>
            ))}
          </tr></thead>
          <tbody>{rows.map((row, i) => (
            <tr key={i} className="border-b dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
              {columns.map(col => <td key={col.key} className="px-3 py-2">{String(row[col.key] ?? "")}</td>)}
            </tr>
          ))}</tbody>
        </table>
      </div>
      <div className="flex items-center justify-between text-xs text-gray-400">
        <span>{total} items</span>
        <div className="flex gap-1">
          <button onClick={() => onPageChange(page - 1)} disabled={page <= 1} className="rounded border px-2 py-1 disabled:opacity-30 dark:border-gray-700">←</button>
          <span className="px-2 py-1">{page}/{totalPages}</span>
          <button onClick={() => onPageChange(page + 1)} disabled={page >= totalPages} className="rounded border px-2 py-1 disabled:opacity-30 dark:border-gray-700">→</button>
        </div>
      </div>
    </div>
  );
}
