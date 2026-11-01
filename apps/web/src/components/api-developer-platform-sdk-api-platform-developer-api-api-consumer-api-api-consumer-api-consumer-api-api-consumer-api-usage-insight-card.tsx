"use client";

interface Insight { id: string; category: string; severity: string; title: string; description: string; recommendation: string; }
interface Props { insights: Insight[]; consumerId: string; appName: string; }

const severityColors: Record<string, string> = {
  critical: "border-l-red-500 bg-red-50 dark:bg-red-900/10",
  warning: "border-l-amber-500 bg-amber-50 dark:bg-amber-900/10",
  info: "border-l-blue-500 bg-blue-50 dark:bg-blue-900/10",
};
const catIcons: Record<string, string> = { optimization: "⚡", security: "🔒", cost: "💰", performance: "🏎️", adoption: "📈" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiUsageInsightCard({ insights, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💡 Usage Insights</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {insights.length} insights</p>
      </div>
      {insights.length === 0 ? (
        <p className="text-center text-sm text-green-500">All good — no issues detected</p>
      ) : (
        <div className="space-y-2">
          {insights.map((i) => (
            <div key={i.id} className={`rounded-lg border-l-4 p-2 ${severityColors[i.severity] ?? ""}`}>
              <div className="flex items-center gap-1 text-[11px] font-medium text-gray-700 dark:text-gray-300">
                <span>{catIcons[i.category] ?? "📋"}</span>
                <span>{i.title}</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-500">{i.description}</div>
              <div className="mt-0.5 text-[10px] text-blue-600 dark:text-blue-400">💡 {i.recommendation}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
