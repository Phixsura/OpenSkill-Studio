"use client";

interface WebhookPayloadPreviewProps { payload: Record<string, unknown>; eventType: string; valid: boolean; }

export function WebhookPayloadPreview({ payload, eventType, valid }: WebhookPayloadPreviewProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Webhook Payload</h3>
        <div className="flex items-center gap-2">
          <code className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">{eventType}</code>
          <span className={`text-xs ${valid ? "text-green-600" : "text-red-600"}`}>{valid ? "✓ Valid" : "✗ Invalid"}</span>
        </div>
      </div>
      <pre className="rounded-lg bg-gray-950 p-3 text-xs font-mono text-green-400 overflow-x-auto max-h-64">
        {JSON.stringify(payload, null, 2)}
      </pre>
    </div>
  );
}
