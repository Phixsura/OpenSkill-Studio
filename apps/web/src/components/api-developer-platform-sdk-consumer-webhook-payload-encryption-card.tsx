"use client";

interface Config { webhookId: string; algorithm: string; keyVersion: number; enabled: boolean; }
interface Props { configs: Config[]; consumerId: string; appName: string; }

const algColors: Record<string, string> = {
  "aes-256-gcm": "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  "aes-256-cbc": "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  none: "bg-gray-200 text-gray-500",
};

export default function APIDeveloperPlatformSDKConsumerWebhookPayloadEncryptionCard({ configs, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔐 Payload Encryption</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No encryption configured</p>
      ) : (
        <div className="space-y-1">
          {configs.map((c) => (
            <div key={c.webhookId} className={`flex items-center justify-between rounded bg-gray-50 px-2 py-1.5 text-[11px] dark:bg-gray-800 ${!c.enabled ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-2">
                <code className="text-gray-700 dark:text-gray-300">{c.webhookId}</code>
                <span className={`rounded px-1.5 py-0.5 text-[9px] font-medium ${algColors[c.algorithm] ?? ""}`}>{c.algorithm}</span>
              </div>
              <span className="text-[10px] text-gray-400">v{c.keyVersion}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
