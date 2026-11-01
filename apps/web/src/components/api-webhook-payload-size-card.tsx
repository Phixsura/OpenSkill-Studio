"use client";

interface SizeStats { destination: string; avg_bytes: number; max_bytes: number; over_limit_count: number; delivery_count: number; }
interface APIWebhookPayloadSizeCardProps { stats: SizeStats[]; maxLimit: number; appName: string; }

function fmt(b: number): string { if (b < 1024) return `${b}B`; if (b < 1048576) return `${(b/1024).toFixed(1)}KB`; return `${(b/1048576).toFixed(1)}MB`; }

export default function APIWebhookPayloadSizeCard({ stats, maxLimit, appName }: APIWebhookPayloadSizeCardProps) {
  const overLimit = stats.filter((s) => s.over_limit_count > 0).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📏 Payload Size</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · max {fmt(maxLimit)}</p>
        </div>
        {overLimit > 0 && <span className="text-[10px] text-red-500">{overLimit} over limit</span>}
      </div>
      {stats.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No payload data</p>
      ) : (
        <div className="space-y-1">
          {stats.map((s) => (
            <div key={s.destination} className="flex items-center justify-between text-[11px]">
              <span className="truncate max-w-[150px] text-gray-700 dark:text-gray-300">{s.destination}</span>
              <span className="text-gray-400">avg {fmt(s.avg_bytes)} · max {fmt(s.max_bytes)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
