"use client";

interface AppColumn { id: string; name: string; icon: string; }
interface CellValue { value: unknown; display: string; type: string; }
interface FeatureRow { feature: string; values: Record<string, CellValue>; }
interface FeatureComparisonGridProps { columns: AppColumn[]; rows: FeatureRow[]; }

export function FeatureComparisonGrid({ columns, rows }: FeatureComparisonGridProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b dark:border-gray-700">
            <th className="px-4 py-3 text-left font-medium">Feature</th>
            {columns.map(c => (
              <th key={c.id} className="px-4 py-3 text-center">
                <span className="mr-1">{c.icon}</span>{c.name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-b dark:border-gray-800">
              <td className="px-4 py-2.5 font-medium">{r.feature}</td>
              {columns.map(c => {
                const cell = r.values[c.id];
                return (
                  <td key={c.id} className="px-4 py-2.5 text-center">
                    <span className={cell?.type === "bool" ? (cell.value ? "text-green-600" : "text-gray-300") : ""}>{cell?.display ?? "—"}</span>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
