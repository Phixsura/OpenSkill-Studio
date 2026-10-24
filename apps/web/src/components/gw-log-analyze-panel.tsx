"use client";
interface TopPath { path: string; count: number; }
interface GwLogAnalyzePanelProps { total: number; avgMs: number; slowRequests: number;
  byStatus: Record<string, number>; topPaths: TopPath[]; }
export function GwLogAnalyzePanel({ total, avgMs, slowRequests, byStatus, topPaths }: GwLogAnalyzePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Gateway Log Analysis</h3>
        <span className="text-xs text-gray-400">{total.toLocaleString()} reqs · {avgMs}ms avg · {slowRequests} slow</span>
      </div>
      <div className="flex gap-2 p-3 text-xs">
        {Object.entries(byStatus).map(([s, c]) => (
          <span key={s} className={`px-1.5 py-0.5 rounded ${s === "5xx" ? "bg-red-100 text-red-700" : "bg-gray-100 dark:bg-gray-800"}`}>{s}: {c}</span>
        ))}
      </div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {topPaths.map(p => (
          <div key={p.path} className="flex justify-between px-4 py-1 text-xs">
            <span className="font-mono">{p.path}</span>
            <span className="text-gray-400">{p.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
