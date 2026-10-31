"use client";

interface StatsInfo { destination: string; total_payloads: number; avg_bytes: number; max_bytes: number; oversized_count: number; }
interface Props { stats: StatsInfo[]; totalBandwidth: number; appName: string; }

function fmtSize(b: number) { return b < 1024 ? `${b}B` : b < 1048576 ? `${(b/1024).toFixed(1)}KB` : `${(b/1048576).toFixed(1)}MB`; }

export default function APIDeveloperAPIApiDeveloperApiApiWebhookPayloadSizeAnalyzerCard({ stats, totalBandwidth, appName }: Props) {
  const oversizedTotal = stats.reduce((s, st) => s + st.oversized_count, 0);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📏 Payload Sizes</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {fmtSize(totalBandwidth)} total</p>
        </div>
        {oversizedTotal > 0 && <span className="rounded-full bg-orange-100 px-2 py-0.5 text-[10px] text-orange-700">{oversizedTotal} oversized</span>}
      </div>
      {stats.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No payload data</p>
      ) : (
        <div className="space-y-1.5">
          {stats.map((s) => (
            <div key={s.destination} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{new URL(s.destination).hostname}</span>
              <span className="text-gray-400">avg: {fmtSize(s.avg_bytes)} · max: {fmtSize(s.max_bytes)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
