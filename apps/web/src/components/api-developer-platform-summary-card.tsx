"use client";

interface SummaryInfo {
  total_developers: number; active_developers_30d: number;
  total_api_calls_30d: number; api_error_rate: number; avg_latency_ms: number;
  webhook_success_rate: number; webhook_destinations: number;
  documentation_coverage_pct: number; onboarding_completion_pct: number;
  developer_satisfaction: number; open_incidents: number; open_support_tickets: number;
}
interface Props { summary: SummaryInfo; healthGrade: string; appName: string; }

const gradeColor: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-red-500" };

export default function APIDeveloperPlatformSummaryCard({ summary: s, healthGrade, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌟 Platform Summary</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-3xl font-bold ${gradeColor[healthGrade] ?? "text-gray-500"}`}>{healthGrade}</span>
      </div>
      <div className="grid grid-cols-4 gap-1.5 text-center">
        {[
          { l: "Developers", v: s.total_developers },
          { l: "Active 30d", v: s.active_developers_30d },
          { l: "API Calls", v: s.total_api_calls_30d.toLocaleString() },
          { l: "Error Rate", v: `${s.api_error_rate}%` },
          { l: "Latency", v: `${s.avg_latency_ms}ms` },
          { l: "Webhooks", v: `${s.webhook_success_rate}%` },
          { l: "Docs", v: `${s.documentation_coverage_pct}%` },
          { l: "Satisfaction", v: `${s.developer_satisfaction}/5` },
          { l: "Incidents", v: s.open_incidents },
          { l: "Tickets", v: s.open_support_tickets },
          { l: "Onboarding", v: `${s.onboarding_completion_pct}%` },
          { l: "Destinations", v: s.webhook_destinations },
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
