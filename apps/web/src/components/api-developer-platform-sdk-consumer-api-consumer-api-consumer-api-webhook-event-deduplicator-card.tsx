"use client";

interface Props { trackedFingerprints: number; ttlHours: number; maxEntries: number; duplicatesBlocked: number; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiWebhookEventDeduplicatorCard({ trackedFingerprints, ttlHours, maxEntries, duplicatesBlocked, consumerId, appName }: Props) {
  const usagePct = maxEntries > 0 ? Math.round((trackedFingerprints / maxEntries) * 100) : 0;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Event Deduplication</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · TTL: {ttlHours}h</p>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-[11px]">
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{trackedFingerprints.toLocaleString()}</div><div className="text-[9px] text-gray-400">Tracked</div></div>
        <div className="rounded bg-green-50 p-1.5 dark:bg-green-900/20"><div className="font-bold text-green-600">{duplicatesBlocked}</div><div className="text-[9px] text-gray-400">Blocked</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{usagePct}%</div><div className="text-[9px] text-gray-400">Capacity</div></div>
      </div>
      <div className="h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-full rounded-full ${usagePct >= 90 ? "bg-red-500" : "bg-blue-500"}`} style={{ width: `${Math.min(usagePct, 100)}%` }} />
      </div>
    </div>
  );
}
