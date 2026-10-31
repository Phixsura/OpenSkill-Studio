"use client";

interface Props { activeKeys: number; duplicatesBlocked: number; appName: string; }

export default function APIDeveloperPlatformSDKApiDeveloperApiWebhookIdempotencyCard({ activeKeys, duplicatesBlocked, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 Webhook Idempotency</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="grid grid-cols-2 gap-3 text-center">
        <div className="rounded bg-gray-50 py-3 dark:bg-gray-800">
          <p className="text-xl font-bold text-blue-600">{activeKeys.toLocaleString()}</p>
          <p className="text-[9px] text-gray-400">Active Keys</p>
        </div>
        <div className="rounded bg-gray-50 py-3 dark:bg-gray-800">
          <p className="text-xl font-bold text-green-600">{duplicatesBlocked.toLocaleString()}</p>
          <p className="text-[9px] text-gray-400">Duplicates Blocked</p>
        </div>
      </div>
    </div>
  );
}
