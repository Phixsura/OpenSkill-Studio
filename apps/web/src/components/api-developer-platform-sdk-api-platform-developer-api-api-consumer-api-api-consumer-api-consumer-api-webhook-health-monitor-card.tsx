"use client";

interface Summary { webhookId: string; status: string; uptimePct: number; avgResponseMs: number; consecutiveFailures: number; totalChecks: number; }
interface Props { summaries: Summary[]; consumerId: string; appName: string; }

const statusColors: Record<string, string> = {
  healthy: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  degraded: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  down: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  unknown: "bg-gray-200 text-gray-500 dark:bg-gray-700 dark:text-gray-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookHealthMonitorCard({ summaries, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💓 Webhook Health</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {summaries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No webhooks monitored</p>
      ) : (
        <div className="space-y-2">
          {summaries.map((s) => (
            <div key={s.webhookId} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <code className="text-gray-700 dark:text-gray-300">{s.webhookId}</code>
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${statusColors[s.status] ?? ""}`}>{s.status}</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">
                {s.uptimePct}% uptime · {s.avgResponseMs}ms avg · {s.totalChecks} checks
                {s.consecutiveFailures > 0 && <span className="text-red-400"> · {s.consecutiveFailures} consecutive fails</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
