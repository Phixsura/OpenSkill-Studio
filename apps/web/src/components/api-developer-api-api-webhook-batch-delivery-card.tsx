"use client";

interface StatsInfo { batches_sent: number; events_batched: number; pending: number; }
interface Props { stats: StatsInfo; appName: string; }

export default function APIDeveloperAPIApiWebhookBatchDeliveryCard({ stats, appName }: Props) {
  const avgBatchSize = stats.batches_sent > 0 ? Math.round(stats.events_batched / stats.batches_sent) : 0;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📦 Batch Delivery</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="grid grid-cols-4 gap-2 text-center">
        {[
          { l: "Batches", v: stats.batches_sent },
          { l: "Events", v: stats.events_batched.toLocaleString() },
          { l: "Pending", v: stats.pending },
          { l: "Avg Size", v: avgBatchSize },
        ].map((m) => (
          <div key={m.l} className="rounded bg-gray-50 py-1.5 dark:bg-gray-800">
            <p className="text-[12px] font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
            <p className="text-[8px] text-gray-400">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
