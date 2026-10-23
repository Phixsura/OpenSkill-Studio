"use client";

interface ComparisonRow { id: string; name: string; [feature: string]: unknown; }
interface FeatureComparisonTableProps { matrix: ComparisonRow[]; features: string[];
  winnerId: string | null; }

export function FeatureComparisonTable({ matrix, features, winnerId }: FeatureComparisonTableProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Feature Comparison</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b dark:border-gray-700">
              <th className="pb-2 text-left">Feature</th>
              {matrix.map(item => (
                <th key={item.id} className="pb-2 text-center">
                  <span className={item.id === winnerId ? "text-blue-600 font-bold" : ""}>{item.name as string}</span>
                  {item.id === winnerId && <span className="ml-1 text-xs">🏆</span>}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {features.map(feat => (
              <tr key={feat} className="border-b dark:border-gray-800">
                <td className="py-2 capitalize">{feat.replace(/_/g, " ")}</td>
                {matrix.map(item => (
                  <td key={item.id} className="py-2 text-center">
                    <span className={item[feat] ? "text-green-500" : "text-gray-300"}>{item[feat] ? "✓" : "—"}</span>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
