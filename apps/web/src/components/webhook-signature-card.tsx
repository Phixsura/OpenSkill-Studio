"use client";

interface SigningKeyInfo {
  key_id: string;
  active: boolean;
}

interface WebhookSignatureCardProps {
  keys: SigningKeyInfo[];
  appName: string;
}

export default function WebhookSignatureCard({ keys, appName }: WebhookSignatureCardProps) {
  const active = keys.filter((k) => k.active).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🔏 Webhook Signatures
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {active} active / {keys.length} total
        </span>
      </div>

      {keys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No signing keys</p>
      ) : (
        <div className="space-y-1.5">
          {keys.map((k) => (
            <div
              key={k.key_id}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <span className="font-mono text-xs text-gray-700 dark:text-gray-300">{k.key_id}</span>
              <span
                className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${
                  k.active
                    ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                    : "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400"
                }`}
              >
                {k.active ? "active" : "inactive"}
              </span>
            </div>
          ))}
        </div>
      )}

      <p className="mt-3 text-center text-[10px] text-gray-400">HMAC-SHA256</p>
    </div>
  );
}
