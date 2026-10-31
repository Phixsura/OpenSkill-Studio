"use client";

interface DeliveryResult { eventId: string; endpoint: string; statusCode: number;
  responseMs: number; delivered: boolean; }
interface WebhookSandboxProps { results: DeliveryResult[]; successRate: number;
  avgResponseMs: number; onSendTest: () => void; }

export function WebhookSandbox({ results, successRate, avgResponseMs, onSendTest }: WebhookSandboxProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🧪 Webhook Sandbox</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{successRate}% success · {avgResponseMs}ms avg</span>
          <button onClick={onSendTest} className="px-3 py-1 text-xs bg-blue-500 text-white rounded">Send Test</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-40 overflow-y-auto">
        {results.map(r => (
          <div key={r.eventId} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span>{r.delivered ? "✅" : "❌"}</span>
              <span className="font-mono">{r.eventId}</span>
            </div>
            <div className="flex gap-2 text-gray-400">
              <span className={r.statusCode < 400 ? "" : "text-red-500"}>{r.statusCode}</span>
              <span>{r.responseMs}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
