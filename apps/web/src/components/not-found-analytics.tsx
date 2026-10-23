"use client";

interface TopPath { path: string; count: number; }
interface TopReferrer { referrer: string; count: number; }
interface NotFoundAnalyticsProps { total: number; uniquePaths: number;
  topPaths: TopPath[]; topReferrers: TopReferrer[]; needsAttention: boolean; }

export function NotFoundAnalytics({ total, uniquePaths, topPaths, topReferrers, needsAttention }: NotFoundAnalyticsProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">404 Analytics</h3>
        <div className="flex items-center gap-2">
          {needsAttention && <span className="text-xs text-red-600">⚠ Needs attention</span>}
          <span className="text-xs text-gray-400">{total} total · {uniquePaths} unique</span>
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <p className="text-xs font-semibold text-gray-400 mb-2">Top Missing Pages</p>
          <div className="space-y-1">
            {topPaths.map(p => (
              <div key={p.path} className="flex items-center justify-between text-sm">
                <code className="text-xs font-mono truncate max-w-[150px]">{p.path}</code>
                <span className="text-xs text-gray-400">{p.count}×</span>
              </div>
            ))}
          </div>
        </div>
        <div>
          <p className="text-xs font-semibold text-gray-400 mb-2">Top Referrers</p>
          <div className="space-y-1">
            {topReferrers.map(r => (
              <div key={r.referrer} className="flex items-center justify-between text-sm">
                <span className="text-xs truncate max-w-[150px]">{r.referrer}</span>
                <span className="text-xs text-gray-400">{r.count}×</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
