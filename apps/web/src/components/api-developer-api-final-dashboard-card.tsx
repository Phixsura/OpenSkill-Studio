"use client";

interface DashInfo {
  platform_health_grade: string; api_performance_grade: string; webhook_delivery_grade: string;
  developer_experience_grade: string; documentation_grade: string; security_grade: string;
  overall_grade: string; total_developers: number; total_api_calls: number; overall_uptime: number; nps_score: number;
}
interface Props { dashboard: DashInfo; appName: string; }

const gColor: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-red-500" };

export default function APIDeveloperAPIFinalDashboardCard({ dashboard: d, appName }: Props) {
  return (
    <div className="rounded-xl border-2 border-blue-200 bg-white p-5 shadow-md dark:border-blue-800 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100">🏆 Developer Platform Dashboard</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — Complete Platform Overview</p>
        </div>
        <div className="text-center">
          <span className={`text-4xl font-black ${gColor[d.overall_grade] ?? "text-gray-500"}`}>{d.overall_grade}</span>
          <p className="text-[9px] text-gray-400">Overall</p>
        </div>
      </div>
      <div className="mb-3 grid grid-cols-6 gap-1 text-center">
        {[
          { l: "Health", v: d.platform_health_grade },
          { l: "Performance", v: d.api_performance_grade },
          { l: "Webhooks", v: d.webhook_delivery_grade },
          { l: "Dev XP", v: d.developer_experience_grade },
          { l: "Docs", v: d.documentation_grade },
          { l: "Security", v: d.security_grade },
        ].map((m) => (
          <div key={m.l} className="rounded bg-gray-50 py-1 dark:bg-gray-800">
            <p className={`text-sm font-bold ${gColor[m.v] ?? "text-gray-500"}`}>{m.v}</p>
            <p className="text-[6px] text-gray-500">{m.l}</p>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-4 gap-1 text-center">
        {[
          { l: "Developers", v: d.total_developers.toLocaleString() },
          { l: "API Calls", v: d.total_api_calls.toLocaleString() },
          { l: "Uptime", v: `${d.overall_uptime}%` },
          { l: "NPS", v: d.nps_score },
        ].map((m) => (
          <div key={m.l} className="rounded bg-gray-50 py-1 dark:bg-gray-800">
            <p className="text-xs font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
            <p className="text-[7px] text-gray-500">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
