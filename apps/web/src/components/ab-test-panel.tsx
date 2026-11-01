"use client";

interface VariantResult { id: string; name: string; impressions: number; conversions: number; conversion_rate: number; }
interface AbTestPanelProps { results: VariantResult[]; winner: string | null; totalImpressions: number; }

export function AbTestPanel({ results, winner, totalImpressions }: AbTestPanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">A/B Test Results</h3>
        <span className="text-xs text-gray-400">{totalImpressions.toLocaleString()} impressions</span>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        {results.map(v => (
          <div key={v.id} className={`rounded-lg border p-4 ${v.id === winner ? "border-green-500 bg-green-50 dark:bg-green-900/10" : "dark:border-gray-700"}`}>
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold">{v.name}</span>
              {v.id === winner && <span className="text-xs text-green-600 font-medium">🏆 Winner</span>}
            </div>
            <p className="mt-2 text-2xl font-bold">{v.conversion_rate}%</p>
            <p className="text-xs text-gray-400">{v.conversions.toLocaleString()} / {v.impressions.toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
