"use client";

interface AppInfo { id: string; name: string; }
interface ComparisonRow { criterion: string; [appId: string]: unknown; }
interface AppComparisonSideBySideProps { apps: AppInfo[]; rows: ComparisonRow[];
  scores: Record<string, number>; winner: string | null; }

const criteriaLabels: Record<string, string> = {
  rating: "⭐ Rating", installs: "📥 Installs", price: "💰 Price",
  has_api: "🔌 API", has_docs: "📚 Docs", has_support: "💬 Support",
};

export function AppComparisonSideBySide({ apps, rows, scores, winner }: AppComparisonSideBySideProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Compare Apps</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b dark:border-gray-700">
              <th className="pb-2 text-left"></th>
              {apps.map(a => (
                <th key={a.id} className="pb-2 text-center">
                  <span className={a.id === winner ? "font-bold text-blue-600" : ""}>{a.name}</span>
                  {a.id === winner && <span className="ml-1">🏆</span>}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map(row => (
              <tr key={row.criterion} className="border-b dark:border-gray-800">
                <td className="py-2 text-gray-500">{criteriaLabels[row.criterion] ?? row.criterion}</td>
                {apps.map(a => (
                  <td key={a.id} className="py-2 text-center font-medium">
                    {typeof row[a.id] === "boolean" ? (row[a.id] ? "✅" : "❌") : String(row[a.id] ?? "—")}
                  </td>
                ))}
              </tr>
            ))}
            <tr className="font-bold">
              <td className="pt-2">Score</td>
              {apps.map(a => (
                <td key={a.id} className={`pt-2 text-center ${a.id === winner ? "text-blue-600" : ""}`}>
                  {scores[a.id]}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
