"use client";

interface TestResultInfo {
  test_id: string;
  destination: string;
  status_code: number | null;
  duration_ms: number;
  success: boolean;
  error: string;
}

interface APIWebhookTestCardProps {
  results: TestResultInfo[];
  appName: string;
}

export default function APIWebhookTestCard({ results, appName }: APIWebhookTestCardProps) {
  const passed = results.filter((r) => r.success).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🧪 Webhook Tests</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{passed}/{results.length} passed</span>
      </div>

      {results.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No test results</p>
      ) : (
        <div className="space-y-1">
          {results.map((r) => (
            <div key={r.test_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${r.success ? "bg-green-500" : "bg-red-500"}`} />
                <span className="truncate max-w-[160px] text-gray-700 dark:text-gray-300">{r.destination}</span>
              </div>
              <span className="text-gray-400">{r.status_code ?? "err"} · {r.duration_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
