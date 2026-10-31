"use client";

interface ExtInfo { id: string; name: string; rating: number; installs: number; priceCents: number; featureCount: number; avgLatencyMs: number; }
interface Winners { rating: string; installs: string; price: string; performance: string; }

function fmt(cents: number) { return cents === 0 ? "Free" : `$${(cents/100).toFixed(2)}`; }

export function ExtensionComparisonPanel({ extensions, winners, recommended, featureMatrix }: {
  extensions: ExtInfo[]; winners: Winners; recommended: string;
  featureMatrix: Record<string, Record<string, boolean>>;
}) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">⚖️ Extension Comparison</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="border-b dark:border-gray-700">
            <th className="text-left py-2">Metric</th>
            {extensions.map((e) => (
              <th key={e.id} className="text-center py-2">
                <span className="font-bold">{e.name}</span>
                {e.id === recommended && <span className="text-xs text-green-600 block">★ Recommended</span>}
              </th>
            ))}
          </tr></thead>
          <tbody>
            <tr className="border-b dark:border-gray-700">
              <td className="py-1.5">Rating</td>
              {extensions.map((e) => (
                <td key={e.id} className={`text-center ${e.id === winners.rating ? "font-bold text-green-600" : ""}`}>★ {e.rating}</td>
              ))}
            </tr>
            <tr className="border-b dark:border-gray-700">
              <td className="py-1.5">Installs</td>
              {extensions.map((e) => (
                <td key={e.id} className={`text-center ${e.id === winners.installs ? "font-bold text-green-600" : ""}`}>{e.installs.toLocaleString()}</td>
              ))}
            </tr>
            <tr className="border-b dark:border-gray-700">
              <td className="py-1.5">Price</td>
              {extensions.map((e) => (
                <td key={e.id} className={`text-center ${e.id === winners.price ? "font-bold text-green-600" : ""}`}>{fmt(e.priceCents)}</td>
              ))}
            </tr>
            <tr className="border-b dark:border-gray-700">
              <td className="py-1.5">Features</td>
              {extensions.map((e) => <td key={e.id} className="text-center">{e.featureCount}</td>)}
            </tr>
          </tbody>
        </table>
      </div>
      {Object.keys(featureMatrix).length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-1">Feature Matrix</h3>
          <div className="space-y-0.5 text-xs">
            {Object.entries(featureMatrix).map(([feat, support]) => (
              <div key={feat} className="flex items-center gap-2">
                <span className="w-24">{feat}</span>
                {extensions.map((e) => (
                  <span key={e.id} className="w-20 text-center">{support[e.id] ? "✅" : "❌"}</span>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
