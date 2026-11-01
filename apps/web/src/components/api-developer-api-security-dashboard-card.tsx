"use client";

interface DashInfo { security_score: number; total_findings: number; critical_findings: number; high_findings: number; resolved_findings: number; active_api_keys: number; expired_keys: number; ip_rules: number; cors_policies: number; }
interface Props { dashboard: DashInfo; isSecure: boolean; appName: string; }

export default function APIDeveloperAPISecurityDashboardCard({ dashboard: d, isSecure, appName }: Props) {
  const scoreColor = d.security_score >= 90 ? "text-green-600" : d.security_score >= 70 ? "text-yellow-600" : "text-red-500";
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🛡️ Security Dashboard</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className={`text-2xl font-bold ${scoreColor}`}>{d.security_score}</span>
          <p className={`text-[10px] font-medium ${isSecure ? "text-green-600" : "text-red-500"}`}>{isSecure ? "Secure" : "Issues found"}</p>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-1.5 text-center">
        {[
          { l: "Findings", v: d.total_findings },
          { l: "Critical", v: d.critical_findings },
          { l: "Resolved", v: d.resolved_findings },
          { l: "API Keys", v: d.active_api_keys },
          { l: "IP Rules", v: d.ip_rules },
          { l: "CORS", v: d.cors_policies },
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
