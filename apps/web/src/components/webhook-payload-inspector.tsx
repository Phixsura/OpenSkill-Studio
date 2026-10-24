"use client";

interface WebhookPayloadInspectorProps { payload: Record<string, unknown>; sizeBytes: number; withinLimit: boolean; }

export function WebhookPayloadInspector({ payload, sizeBytes, withinLimit }: WebhookPayloadInspectorProps) {
  const formatSize = (b: number) => b < 1024 ? `${b}B` : `${(b / 1024).toFixed(1)}KB`;
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between border-b p-3 dark:border-gray-700">
        <h3 className="text-sm font-semibold">Payload Inspector</h3>
        <span className={`text-xs ${withinLimit ? "text-green-600" : "text-red-600"}`}>
          {formatSize(sizeBytes)} {withinLimit ? "✅" : "⚠️ Over limit"}
        </span>
      </div>
      <pre className="max-h-48 overflow-auto p-3 text-xs font-mono text-gray-700 dark:text-gray-300">
        {JSON.stringify(payload, null, 2)}
      </pre>
    </div>
  );
}
