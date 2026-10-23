"use client";

interface App { id: string; name: string; }
interface Row { dimension: string; icon: string; values: Record<string, unknown>; winner?: string; }
interface ComparisonTableV2Props { apps: App[]; rows: Row[]; }

export function ComparisonTableV2({ apps, rows }: ComparisonTableV2Props) {
  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th className="px-4 py-3 text-left font-medium">Feature</th>
            {apps.map(a => <th key={a.id} className="px-4 py-3 text-center font-medium">{a.name}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map(row => (
            <tr key={row.dimension} className="border-t dark:border-gray-700">
              <td className="px-4 py-2.5">{row.icon} {row.dimension}</td>
              {apps.map(a => (
                <td key={a.id} className={`px-4 py-2.5 text-center ${row.winner === a.id ? "font-bold text-green-600" : ""}`}>
                  {String(row.values[a.id] ?? "N/A")}
                  {row.winner === a.id && " 🏆"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
