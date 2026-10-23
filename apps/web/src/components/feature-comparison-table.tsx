"use client";

interface MatrixRow { feature: string; values: Record<string, boolean>; }
interface FeatureComparisonTableProps { products: string[]; matrix: MatrixRow[];
  scores: Record<string, { total: number; pct: number }>; bestMatch: string; }

export function FeatureComparisonTable({ products, matrix, scores, bestMatch }: FeatureComparisonTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Feature Comparison</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="border-b dark:border-gray-700">
            <th className="p-3 text-left text-xs text-gray-400">Feature</th>
            {products.map(p => (
              <th key={p} className="p-3 text-center">
                <span className="font-medium">{p}</span>
                {p === bestMatch && <span className="block text-xs text-green-600">🏆 Best</span>}
              </th>
            ))}
          </tr></thead>
          <tbody>
            {matrix.map(row => (
              <tr key={row.feature} className="border-b last:border-0 dark:border-gray-700">
                <td className="p-3 capitalize">{row.feature.replace("_", " ")}</td>
                {products.map(p => (
                  <td key={p} className="p-3 text-center text-lg">
                    {row.values[p] ? "✅" : "❌"}
                  </td>
                ))}
              </tr>
            ))}
            <tr className="bg-gray-50 dark:bg-gray-800 font-medium">
              <td className="p-3">Score</td>
              {products.map(p => (
                <td key={p} className="p-3 text-center">{scores[p]?.pct}%</td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
