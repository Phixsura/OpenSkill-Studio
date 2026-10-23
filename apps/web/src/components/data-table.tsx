"use client";

interface Column { key: string; label: string; }
interface DataTableProps { columns: Column[]; rows: Record<string, unknown>[]; totalRows: number;
  page: number; totalPages: number; sortBy: string | null; sortDir: string;
  onSort: (key: string) => void; onPage: (page: number) => void; }

export function DataTable({ columns, rows, totalRows, page, totalPages, sortBy, sortDir, onSort, onPage }: DataTableProps) {
  return (
    <div className="space-y-3">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b dark:border-gray-700">
              {columns.map(col => (
                <th key={col.key} className="cursor-pointer pb-2 text-left font-medium" onClick={() => onSort(col.key)}>
                  {col.label} {sortBy === col.key && (sortDir === "asc" ? "↑" : "↓")}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i} className="border-b dark:border-gray-800">
                {columns.map(col => (
                  <td key={col.key} className="py-2">{String(row[col.key] ?? "")}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex items-center justify-between text-xs text-gray-400">
        <span>{totalRows} rows</span>
        <div className="flex gap-1">
          {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => i + 1).map(p => (
            <button key={p} onClick={() => onPage(p)}
              className={`rounded px-2 py-1 ${p === page ? "bg-blue-600 text-white" : "border dark:border-gray-600"}`}>
              {p}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
