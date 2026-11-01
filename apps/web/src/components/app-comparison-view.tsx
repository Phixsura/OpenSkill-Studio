"use client";

interface AppColumn { id: string; name: string; icon: string; }
interface MetricRow { metric: string; label: string; values: Record<string, number>; best: string; }
interface AppComparisonViewProps { columns: AppColumn[]; comparison: MetricRow[]; }

export function AppComparisonView({ columns, comparison }: AppComparisonViewProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b dark:border-gray-700">
            <th className="px-4 py-3 text-left font-medium">Metric</th>
            {columns.map(c => (
              <th key={c.id} className="px-4 py-3 text-center">
                <span className="mr-1">{c.icon}</span>{c.name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {comparison.map(row => (
            <tr key={row.metric} className="border-b dark:border-gray-800">
              <td className="px-4 py-2.5 font-medium">{row.label}</td>
              {columns.map(c => {
                const val = row.values[c.id] ?? 0;
                const isBest = c.id === row.best;
                return (
                  <td key={c.id} className={`px-4 py-2.5 text-center ${isBest ? "font-bold text-green-600" : ""}`}>
                    {typeof val === "number" && val % 1 !== 0 ? val.toFixed(1) : val.toLocaleString()}
                    {isBest && " 🏆"}
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
