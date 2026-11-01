"use client";

interface CdnInsightsPanelProps { totalAssets: number; cached: number; hitRatio: number;
  bandwidthSavedPct: number; byType: Record<string, number>;
  suggestions: { asset: string; action: string; reason: string }[]; }

export function CdnInsightsPanel({ totalAssets, cached, hitRatio, bandwidthSavedPct, byType, suggestions }: CdnInsightsPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌐 CDN Insights</h3>
        <span className="text-xs text-gray-400">{totalAssets} assets · {hitRatio}% hit ratio</span>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold">{cached}</div>
          <div className="text-[10px] text-gray-400">Cached</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold">{hitRatio}%</div>
          <div className="text-[10px] text-gray-400">Hit Ratio</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold text-green-600">{bandwidthSavedPct}%</div>
          <div className="text-[10px] text-gray-400">BW Saved</div>
        </div>
      </div>
      {suggestions.length > 0 && (
        <div className="p-3 border-t dark:border-gray-700">
          <div className="text-xs text-gray-400 mb-1">Suggestions</div>
          {suggestions.map((s, i) => (
            <div key={i} className="text-xs py-0.5">💡 <span className="font-mono">{s.asset}</span> — {s.reason}</div>
          ))}
        </div>
      )}
    </div>
  );
}
