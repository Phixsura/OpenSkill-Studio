"use client";

interface WebhookTransformerProps { templateJson: string; payloadJson: string; outputJson: string;
  placeholders: string[]; }

export function WebhookTransformer({ templateJson, payloadJson, outputJson, placeholders }: WebhookTransformerProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">Payload Transformer</h3>
      <div className="grid gap-3 lg:grid-cols-3">
        <div>
          <p className="text-xs font-semibold text-gray-400 mb-1">Template</p>
          <pre className="rounded bg-gray-100 p-2 text-xs font-mono dark:bg-gray-800 overflow-x-auto max-h-40">{templateJson}</pre>
        </div>
        <div>
          <p className="text-xs font-semibold text-gray-400 mb-1">Input</p>
          <pre className="rounded bg-gray-100 p-2 text-xs font-mono dark:bg-gray-800 overflow-x-auto max-h-40">{payloadJson}</pre>
        </div>
        <div>
          <p className="text-xs font-semibold text-gray-400 mb-1">Output</p>
          <pre className="rounded bg-green-50 p-2 text-xs font-mono dark:bg-green-900/10 overflow-x-auto max-h-40">{outputJson}</pre>
        </div>
      </div>
      <div className="flex flex-wrap gap-1">
        {placeholders.map(p => (
          <code key={p} className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">{`{{ ${p} }}`}</code>
        ))}
      </div>
    </div>
  );
}
