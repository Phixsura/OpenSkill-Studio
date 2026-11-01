"use client";

interface OverviewInfo {
  total_services: number; total_endpoints: number; total_developers: number;
  api_health_grade: string; avg_latency_ms: number; uptime_pct: number;
  webhook_success_rate: number; webhook_destinations: number;
  developer_satisfaction_nps: number; onboarding_completion_pct: number;
  security_score: number; open_findings: number;
  documentation_coverage_pct: number; platform_grade: string;
}
interface Props { overview: OverviewInfo; appName: string; }

const gColor: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-red-500" };

export default function APIDeveloperAPICompleteOverviewCard({ overview: o, appName }: Props) {
  return (
    <div className="rounded-xl border-2 border-green-200 bg-white p-5 shadow-lg dark:border-green-800 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100">🌟 Complete Platform Overview</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — Developer Platform SDK</p>
        </div>
        <div className="text-center">
          <span className={`text-4xl font-black ${gColor[o.platform_grade] ?? "text-gray-500"}`}>{o.platform_grade}</span>
          <p className="text-[8px] text-gray-400">Platform Grade</p>
        </div>
      </div>
      <div className="grid grid-cols-4 gap-1.5 text-center">
        {[
          { l: "Services", v: o.total_services },
          { l: "Endpoints", v: o.total_endpoints.toLocaleString() },
          { l: "Developers", v: o.total_developers.toLocaleString() },
          { l: "API Grade", v: o.api_health_grade },
          { l: "Latency", v: `${o.avg_latency_ms}ms` },
          { l: "Uptime", v: `${o.uptime_pct}%` },
          { l: "Webhooks", v: `${o.webhook_success_rate}%` },
          { l: "Destinations", v: o.webhook_destinations },
          { l: "NPS", v: o.developer_satisfaction_nps },
          { l: "Onboarding", v: `${o.onboarding_completion_pct}%` },
          { l: "Security", v: o.security_score },
          { l: "Doc Coverage", v: `${o.documentation_coverage_pct}%` },
        ].map((m) => (
          <div key={m.l} className="rounded bg-gray-50 py-1 dark:bg-gray-800">
            <p className="text-[11px] font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
            <p className="text-[6px] text-gray-500">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
