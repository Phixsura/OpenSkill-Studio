"use client";

interface TestResult { statusCode: number | null; durationMs: number; success: boolean; responseBody?: string; }

interface WebhookTestConsoleProps { lastResult: TestResult | null; onTest: (eventType: string) => void; eventTypes: string[]; }

export function WebhookTestConsole({ lastResult, onTest, eventTypes }: WebhookTestConsoleProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="mb-3 font-semibold">🧪 Webhook Test Console</h4>
      <div className="mb-3 flex flex-wrap gap-2">
        {eventTypes.slice(0, 4).map(et => (
          <button key={et} onClick={() => onTest(et)} className="rounded border px-2 py-1 text-xs hover:bg-gray-100 dark:hover:bg-gray-800">{et}</button>
        ))}
      </div>
      {lastResult && (
        <div className={`rounded p-3 text-sm ${lastResult.success ? "bg-green-50 dark:bg-green-900/20" : "bg-red-50 dark:bg-red-900/20"}`}>
          <p>{lastResult.success ? "✅" : "❌"} HTTP {lastResult.statusCode ?? "—"} · {lastResult.durationMs}ms</p>
        </div>
      )}
    </div>
  );
}
