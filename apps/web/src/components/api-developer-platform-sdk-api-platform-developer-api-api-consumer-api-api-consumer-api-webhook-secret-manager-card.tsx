"use client";

interface SecretInfo { consumer_id: string; masked_value: string; version: number; rotated: boolean; }
interface Props { secrets: SecretInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookSecretManagerCard({ secrets: secs, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔐 Webhook Secrets</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {secs.length} consumers</p>
      </div>
      {secs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No webhook secrets</p>
      ) : (
        <div className="space-y-1">
          {secs.map((s) => (
            <div key={s.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.consumer_id}</span>
              <span className="font-mono text-gray-400">{s.masked_value} · v{s.version}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
