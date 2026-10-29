"use client";

interface OverviewInfo { total_developers: number; total_apps: number; total_api_calls: number; total_webhooks: number; avg_developer_satisfaction: number; onboarding_completion_pct: number; documentation_coverage_pct: number; platform_health_score: number; }
interface Props { overview: OverviewInfo; appName: string; }

export default function APIDeveloperAnalyticsOverviewCard({ overview: o, appName }: Props) {
  const hColor = o.platform_health_score >= 95 ? "text-green-600" : o.platform_health_score >= 80 ? "text-yellow-600" : "text-red-500";
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎯 Analytics Overview</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-2xl font-bold ${hColor}`}>{o.platform_health_score}%</span>
      </div>
      <div className="grid grid-cols-4 gap-2 text-center">
        {[
          { l: "Developers", v: o.total_developers },
          { l: "Apps", v: o.total_apps },
          { l: "API Calls", v: o.total_api_calls.toLocaleString() },
          { l: "Webhooks", v: o.total_webhooks.toLocaleString() },
          { l: "Satisfaction", v: `${o.avg_developer_satisfaction}/5` },
          { l: "Onboarding", v: `${o.onboarding_completion_pct}%` },
          { l: "Doc Coverage", v: `${o.documentation_coverage_pct}%` },
        ].map((m) => (
          <div key={m.l} className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
            <p className="text-xs font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
            <p className="text-[7px] text-gray-500">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
