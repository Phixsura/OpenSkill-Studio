"use client";

interface Variant { id: string; name: string; impressions: number; conversions: number; conversion_rate: number; }
interface AbTestDashboardProps { experimentName: string; variants: Variant[]; winnerId?: string; }

export function AbTestDashboard({ experimentName, variants, winnerId }: AbTestDashboardProps) {
  const maxRate = Math.max(...variants.map(v => v.conversion_rate), 1);
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">A/B Test: {experimentName}</h2>
      <div className="grid gap-3 sm:grid-cols-2">
        {variants.map(v => (
          <div key={v.id} className={`rounded-lg border p-4 ${v.id === winnerId ? "border-green-500 bg-green-50 dark:bg-green-900/10" : "border-gray-200 dark:border-gray-700"}`}>
            <div className="flex items-center justify-between">
              <span className="font-semibold">{v.name}</span>
              {v.id === winnerId && <span className="text-xs text-green-600">🏆 Winner</span>}
            </div>
            <div className="mt-2 space-y-1 text-sm text-gray-500">
              <p>Impressions: {v.impressions.toLocaleString()}</p>
              <p>Conversions: {v.conversions.toLocaleString()}</p>
            </div>
            <div className="mt-2">
              <div className="flex items-center justify-between text-sm">
                <span>Conversion Rate</span>
                <span className="font-bold">{v.conversion_rate}%</span>
              </div>
              <div className="mt-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className="h-full rounded-full bg-blue-500" style={{ width: `${(v.conversion_rate / maxRate) * 100}%` }} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
