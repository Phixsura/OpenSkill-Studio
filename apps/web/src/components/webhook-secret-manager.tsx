"use client";

interface Secret { secretId: string; createdAt: number; expiresAt: number; active: boolean; masked: string; }

export function WebhookSecretManager({ secrets: secs, onRotate }: {
  secrets: Secret[]; onRotate?: () => void;
}) {
  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <h3 className="font-bold text-sm">Webhook Secrets</h3>
        <button onClick={onRotate} className="text-xs bg-blue-500 text-white px-3 py-1 rounded-lg">🔄 Rotate</button>
      </div>
      {secs.map(s => (
        <div key={s.secretId} className={`border rounded-xl p-3 flex items-center justify-between ${
          s.expiresAt > 0 ? "border-yellow-300 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-900/10" : "border-gray-200 dark:border-gray-700"
        }`}>
          <div>
            <code className="text-xs font-mono">{s.masked}</code>
            <span className="text-xs text-gray-500 ml-2">{s.secretId}</span>
          </div>
          <div className="flex items-center gap-2">
            {s.expiresAt > 0 ? (
              <span className="text-xs text-yellow-600">Grace period</span>
            ) : (
              <span className="text-xs text-green-600 font-medium">Active</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
