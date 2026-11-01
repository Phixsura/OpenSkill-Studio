"use client";
interface TopRoute { route: string; count: number; }
interface GwObservPanelProps { total: number; avgMs: number; errorRatePct: number;
  byStatus: Record<string, number>; topRoutes: TopRoute[]; }
export function GwObservPanel({ total, avgMs, errorRatePct, byStatus, topRoutes }: GwObservPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔭 Gateway Observability</h3>
        <span className="text-xs text-gray-400">{total.toLocaleString()} reqs · {avgMs}ms avg · {errorRatePct}% err</span>
      </div>
      <div className="flex gap-2 p-3 text-xs">
        {Object.entries(byStatus).map(([s, c]) => (
          <span key={s} className={`px-1.5 py-0.5 rounded ${s === "5xx" ? "bg-red-100 text-red-700" : "bg-gray-100 dark:bg-gray-800"}`}>{s}: {c}</span>
        ))}
      </div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {topRoutes.map(r => (
          <div key={r.route} className="flex justify-between px-4 py-1 text-xs">
            <span className="font-mono">{r.route}</span>
            <span className="text-gray-400">{r.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
