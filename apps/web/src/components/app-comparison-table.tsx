"use client";

interface AppComparisonTableProps {
  apps: { id: string; name: string }[];
  matrix: { feature: string; [appId: string]: boolean | string }[];
}

export function AppComparisonTable({ apps, matrix }: AppComparisonTableProps) {
  if (apps.length < 2) return <p className="text-sm text-gray-500">Select at least 2 apps to compare.</p>;
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b dark:border-gray-700">
            <th className="px-4 py-2 text-left font-medium">Feature</th>
            {apps.map(a => <th key={a.id} className="px-4 py-2 text-center font-medium">{a.name}</th>)}
          </tr>
        </thead>
        <tbody>
          {matrix.map(row => (
            <tr key={row.feature} className="border-b dark:border-gray-700">
              <td className="px-4 py-2">{row.feature}</td>
              {apps.map(a => (
                <td key={a.id} className="px-4 py-2 text-center">
                  {row[a.id] ? <span className="text-green-600">✓</span> : <span className="text-gray-300">—</span>}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
