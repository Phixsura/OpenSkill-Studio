"use client";

interface TestResult { success: boolean; statusCode: number; responsePreview: string;
  durationMs: number; verdict: string; error: string | null; }
interface WebhookTestingPanelProps { payloadJson: string; eventType: string;
  result: TestResult | null; onSendTest: () => void; }

export function WebhookTestingPanel({ payloadJson, eventType, result, onSendTest }: WebhookTestingPanelProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">🧪 Test Webhook</h3>
      <div>
        <p className="text-xs text-gray-400 mb-1">Event: <code className="text-blue-600">{eventType}</code></p>
        <pre className="rounded-lg bg-gray-950 p-3 text-xs font-mono text-green-400 max-h-32 overflow-y-auto">{payloadJson}</pre>
      </div>
      <button onClick={onSendTest} className="rounded bg-blue-600 px-4 py-2 text-sm text-white">Send Test Event</button>
      {result && (
        <div className={`rounded-lg border p-3 ${result.success ? "border-green-300 bg-green-50 dark:bg-green-900/10" : "border-red-300 bg-red-50 dark:bg-red-900/10"}`}>
          <p className="text-sm font-medium">{result.verdict}</p>
          <div className="mt-1 flex gap-3 text-xs text-gray-400">
            <span className="font-mono">{result.statusCode}</span>
            <span>{result.durationMs}ms</span>
          </div>
          {result.error && <p className="mt-1 text-xs text-red-500">{result.error}</p>}
          {result.responsePreview && <pre className="mt-2 rounded bg-gray-100 p-2 text-xs dark:bg-gray-800">{result.responsePreview}</pre>}
        </div>
      )}
    </div>
  );
}
