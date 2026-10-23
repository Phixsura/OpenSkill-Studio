"use client";

interface AppColumn { name: string; icon: string; rating: number; installs: number;
  price: string; featureValues: Record<string, boolean>; }
interface AppCompareTableProps { columns: AppColumn[]; features: string[]; }

export function AppCompareTable({ columns, features }: AppCompareTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b dark:border-gray-700">
            <th className="p-3 text-left text-gray-400">Feature</th>
            {columns.map(c => (
              <th key={c.name} className="p-3 text-center">
                <span className="text-xl">{c.icon}</span>
                <p className="font-bold mt-1">{c.name}</p>
                <p className="text-xs text-gray-400">⭐ {c.rating} · {c.price}</p>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {features.map(f => (
            <tr key={f} className="border-b last:border-0 dark:border-gray-700">
              <td className="p-3 capitalize">{f.replace("_", " ")}</td>
              {columns.map(c => (
                <td key={c.name} className="p-3 text-center text-lg">
                  {c.featureValues[f] ? "✅" : "❌"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
