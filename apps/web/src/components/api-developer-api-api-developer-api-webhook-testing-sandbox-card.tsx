"use client";

interface TestInfo { test_id: string; destination: string; event_type: string; status_code: number; duration_ms: number; success: boolean; }
interface Props { tests: TestInfo[]; successRate: number; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiWebhookTestingSandboxCard({ tests, successRate, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🧪 Webhook Sandbox</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-sm font-bold ${successRate >= 90 ? "text-green-600" : successRate >= 50 ? "text-yellow-600" : "text-red-500"}`}>{successRate}%</span>
      </div>
      {tests.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No test deliveries</p>
      ) : (
        <div className="space-y-1">
          {tests.map((t) => (
            <div key={t.test_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-1.5 w-1.5 rounded-full ${t.success ? "bg-green-500" : "bg-red-500"}`} />
                <span className="text-gray-700 dark:text-gray-300">{t.event_type}</span>
              </div>
              <span className="text-gray-400">{t.status_code} · {t.duration_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
