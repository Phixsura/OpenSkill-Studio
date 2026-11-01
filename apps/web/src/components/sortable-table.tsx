"use client";

import { useState } from "react";

interface Column { key: string; label: string; sortable: boolean; }
interface SortableTableProps { columns: Column[]; rows: Record<string, unknown>[]; }

export function SortableTable({ columns, rows }: SortableTableProps) {
  const [sortBy, setSortBy] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const handleSort = (key: string) => {
    if (sortBy === key) { setSortDir(d => d === "asc" ? "desc" : "asc"); }
    else { setSortBy(key); setSortDir("asc"); }
  };

  const sorted = [...rows].sort((a, b) => {
    if (!sortBy) return 0;
    const av = String(a[sortBy] ?? ""), bv = String(b[sortBy] ?? "");
    const cmp = av.localeCompare(bv, undefined, { numeric: true });
    return sortDir === "asc" ? cmp : -cmp;
  });

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b dark:border-gray-700">
            {columns.map(col => (
              <th key={col.key} className="px-3 py-2 text-left font-medium">
                {col.sortable ? (
                  <button onClick={() => handleSort(col.key)} className="flex items-center gap-1 hover:text-blue-600">
                    {col.label}
                    {sortBy === col.key && <span>{sortDir === "asc" ? "↑" : "↓"}</span>}
                  </button>
                ) : col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((row, i) => (
            <tr key={i} className="border-b dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
              {columns.map(col => <td key={col.key} className="px-3 py-2">{String(row[col.key] ?? "")}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
