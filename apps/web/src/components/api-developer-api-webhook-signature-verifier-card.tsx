"use client";

interface StatsInfo { total: number; valid: number; invalid: number; }
interface Props { stats: StatsInfo; recentResults: { delivery_id: string; valid: boolean; algorithm: string; reason: string; }[]; appName: string; }

export default function APIDeveloperAPIWebhookSignatureVerifierCard({ stats, recentResults, appName }: Props) {
  const validPct = stats.total > 0 ? Math.round(stats.valid / stats.total * 100) : 100;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✅ Signature Verifier</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-lg font-bold ${validPct >= 95 ? "text-green-600" : "text-red-500"}`}>{validPct}%</span>
      </div>
      <div className="mb-3 flex gap-3 text-[10px]">
        <span className="text-gray-400">{stats.total} total</span>
        <span className="text-green-600">{stats.valid} valid</span>
        <span className="text-red-500">{stats.invalid} invalid</span>
      </div>
      {recentResults.length > 0 && (
        <div className="space-y-1">
          {recentResults.map((r) => (
            <div key={r.delivery_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-1.5 w-1.5 rounded-full ${r.valid ? "bg-green-500" : "bg-red-500"}`} />
                <span className="text-gray-700 dark:text-gray-300">{r.delivery_id}</span>
              </div>
              <span className="text-gray-400">{r.algorithm}{!r.valid && r.reason ? ` · ${r.reason}` : ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
