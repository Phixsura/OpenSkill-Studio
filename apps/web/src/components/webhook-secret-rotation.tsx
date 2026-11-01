"use client";

interface WebhookSecretRotationProps { webhookId: string; hasSecret: boolean;
  lastRotated: string; gracePeriod: string; onRotate: () => void; }

export function WebhookSecretRotation({ webhookId, hasSecret, lastRotated, gracePeriod, onRotate }: WebhookSecretRotationProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🔄 Webhook Secret</h3>
      <div className="space-y-2 text-sm mb-4">
        <div className="flex justify-between"><span className="text-gray-400">Webhook</span><span className="font-mono text-xs">{webhookId}</span></div>
        <div className="flex justify-between"><span className="text-gray-400">Status</span><span>{hasSecret ? "✅ Active" : "❌ None"}</span></div>
        <div className="flex justify-between"><span className="text-gray-400">Last Rotated</span><span>{lastRotated}</span></div>
        <div className="flex justify-between"><span className="text-gray-400">Grace Period</span><span>{gracePeriod}</span></div>
      </div>
      <button onClick={onRotate}
        className="w-full py-2 bg-yellow-600 text-white text-sm rounded hover:bg-yellow-700">Rotate Secret</button>
    </div>
  );
}
