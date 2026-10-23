"use client";

interface DataTableProps { rows: Record<string, unknown>[]; columns: string[];
  showing: string; hasNext: boolean; hasPrev: boolean;
  onNext: () => void; onPrev: () => void; }

export function DataTable({ rows, columns, showing, hasNext, hasPrev, onNext, onPrev }: DataTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="text-xs text-gray-400 border-b dark:border-gray-700">
            {columns.map(c => <th key={c} className="p-3 text-left capitalize">{c.replace("_", " ")}</th>)}
          </tr></thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i} className="border-b last:border-0 dark:border-gray-700">
                {columns.map(c => <td key={c} className="p-3">{String(r[c] ?? "")}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex items-center justify-between px-4 py-2 border-t dark:border-gray-700 text-xs text-gray-400">
        <span>{showing}</span>
        <div className="flex gap-1">
          <button onClick={onPrev} disabled={!hasPrev}
            className="px-2 py-1 rounded border disabled:opacity-30 hover:bg-gray-50 dark:hover:bg-gray-800">← Prev</button>
          <button onClick={onNext} disabled={!hasNext}
            className="px-2 py-1 rounded border disabled:opacity-30 hover:bg-gray-50 dark:hover:bg-gray-800">Next →</button>
        </div>
      </div>
    </div>
  );
}
