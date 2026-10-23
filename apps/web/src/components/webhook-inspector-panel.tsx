"use client";

interface WebhookInspectorPanelProps { headers: Record<string, string>; bodyRaw: string;
  bodyParsed: Record<string, unknown> | null; isJson: boolean; statusCode: number;
  success: boolean; durationMs: number; bodySizeBytes: number; }

export function WebhookInspectorPanel({ headers, bodyRaw, bodyParsed, isJson, statusCode,
  success, durationMs, bodySizeBytes }: WebhookInspectorPanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">🔍 Webhook Inspector</h3>
        <div className="flex items-center gap-2 text-xs">
          <span className={success ? "text-green-600" : "text-red-600"}>{statusCode}</span>
          <span className="text-gray-400">{durationMs}ms · {bodySizeBytes}B</span>
        </div>
      </div>
      <div>
        <p className="text-xs font-semibold text-gray-400 mb-1">Headers ({Object.keys(headers).length})</p>
        <div className="rounded-lg bg-gray-100 p-2 dark:bg-gray-800 text-xs font-mono space-y-0.5">
          {Object.entries(headers).map(([k, v]) => (
            <div key={k}><span className="text-blue-600">{k}</span>: <span className="text-gray-500">{v}</span></div>
          ))}
        </div>
      </div>
      <div>
        <p className="text-xs font-semibold text-gray-400 mb-1">Body {isJson && "(JSON)"}</p>
        <pre className="rounded-lg bg-gray-950 p-3 text-xs font-mono text-green-400 max-h-48 overflow-y-auto">
          {isJson && bodyParsed ? JSON.stringify(bodyParsed, null, 2) : bodyRaw}
        </pre>
      </div>
    </div>
  );
}
