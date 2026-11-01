"use client";

interface Plan { id: string; name: string; price: string; recommended: boolean; }
interface CellValue { type: string; value: unknown; display: string; }
interface FeatureRow { feature: string; category: string; values: Record<string, CellValue>; }
interface ComparisonTableProps { plans: Plan[]; features: FeatureRow[]; }

export function ComparisonTable({ plans, features }: ComparisonTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b dark:border-gray-700">
            <th className="px-4 py-3 text-left font-medium">Feature</th>
            {plans.map(p => (
              <th key={p.id} className="px-4 py-3 text-center">
                <div className="font-semibold">{p.name}</div>
                <div className="text-xs text-gray-400">{p.price}</div>
                {p.recommended && <span className="mt-1 inline-block rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">Recommended</span>}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {features.map((f, i) => (
            <tr key={i} className="border-b dark:border-gray-800">
              <td className="px-4 py-2.5 font-medium">{f.feature}</td>
              {plans.map(p => {
                const cell = f.values[p.id];
                return (
                  <td key={p.id} className="px-4 py-2.5 text-center">
                    <span className={cell?.type === "bool" ? (cell.value ? "text-green-600" : "text-gray-300") : ""}>
                      {cell?.display ?? "—"}
                    </span>
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
