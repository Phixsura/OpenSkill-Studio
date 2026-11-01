"use client";

interface Props { newCount: number; duplicateCount: number; duplicateRate: number; retentionHours: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookIdempotencyCard({ newCount, duplicateCount, duplicateRate, retentionHours, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 Webhook Idempotency</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {retentionHours}h retention</p>
        </div>
        <span className="text-[10px] text-gray-400">{duplicateRate}% duplicates</span>
      </div>
      <div className="grid grid-cols-2 gap-3 text-center text-[11px]">
        <div><div className="font-semibold text-green-600 dark:text-green-400">{newCount.toLocaleString()}</div><div className="text-gray-400">New</div></div>
        <div><div className="font-semibold text-amber-600 dark:text-amber-400">{duplicateCount.toLocaleString()}</div><div className="text-gray-400">Duplicates</div></div>
      </div>
    </div>
  );
}
