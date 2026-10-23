"use client";

interface DebugDelivery { payload_size: number; content_type: string; has_signature: boolean;
  signature_valid: boolean | null; timestamp: string; }
interface WebhookDebuggerPanelProps { endpointUrl: string; deliveries: DebugDelivery[];
  totalDeliveries: number; onCopyUrl: () => void; }

export function WebhookDebuggerPanel({ endpointUrl, deliveries, totalDeliveries, onCopyUrl }: WebhookDebuggerPanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Webhook Debugger</h2>
        <span className="text-xs text-gray-400">{totalDeliveries} received</span>
      </div>
      <div className="flex items-center gap-2 rounded bg-gray-900 px-3 py-2 font-mono text-xs text-green-400">
        <span className="flex-1 truncate">{endpointUrl}</span>
        <button onClick={onCopyUrl} className="text-blue-400">Copy</button>
      </div>
      <div className="space-y-1.5">
        {deliveries.map((d, i) => (
          <div key={i} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
            <div className="flex items-center gap-2 text-xs">
              <span className="text-gray-400">{d.timestamp.slice(11, 19)}</span>
              <span>{d.content_type || "unknown"}</span>
              <span className="text-gray-400">{d.payload_size}B</span>
            </div>
            <div className="flex items-center gap-1">
              {d.has_signature && (
                <span className={d.signature_valid ? "text-green-500" : "text-red-500"}>
                  {d.signature_valid ? "✅ sig" : "❌ sig"}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
