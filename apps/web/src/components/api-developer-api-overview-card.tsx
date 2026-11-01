"use client";

interface OverviewInfo {
  total_services: number; total_endpoints: number; total_developers: number; total_consumers: number;
  total_api_calls: number; avg_latency_ms: number; error_rate: number; uptime_pct: number;
  webhook_destinations: number; webhook_success_rate: number;
  sdk_versions: number; documentation_coverage: number; onboarding_rate: number; satisfaction_score: number;
}
interface Props { overview: OverviewInfo; appName: string; }

export default function APIDeveloperAPIOverviewCard({ overview: o, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌐 API Overview</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — Developer Platform SDK</p>
      </div>
      <div className="grid grid-cols-4 gap-1.5 text-center">
        {[
          { l: "Services", v: o.total_services },
          { l: "Endpoints", v: o.total_endpoints.toLocaleString() },
          { l: "Developers", v: o.total_developers },
          { l: "Consumers", v: o.total_consumers },
          { l: "API Calls", v: o.total_api_calls.toLocaleString() },
          { l: "Latency", v: `${o.avg_latency_ms}ms` },
          { l: "Error Rate", v: `${o.error_rate}%` },
          { l: "Uptime", v: `${o.uptime_pct}%` },
          { l: "Webhooks", v: `${o.webhook_success_rate}%` },
          { l: "SDK Versions", v: o.sdk_versions },
          { l: "Doc Coverage", v: `${o.documentation_coverage}%` },
          { l: "Satisfaction", v: `${o.satisfaction_score}/5` },
        ].map((m) => (
          <div key={m.l} className="rounded bg-gray-50 py-1 dark:bg-gray-800">
            <p className="text-[11px] font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
            <p className="text-[7px] text-gray-500">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
