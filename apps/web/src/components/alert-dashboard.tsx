"use client";

interface AlertDashboardProps { active: number; resolved: number;
  criticalCount: number; status: string; bySeverity: Record<string, number>;
  byService: Record<string, number>; }

const STATUS_STYLES: Record<string, { bg: string; label: string; color: string }> = {
  critical: { bg: "bg-red-50 dark:bg-red-900/10", label: "🔴 Critical Alerts", color: "text-red-600" },
  warning: { bg: "bg-yellow-50 dark:bg-yellow-900/10", label: "⚠️ Active Alerts", color: "text-yellow-600" },
  clear: { bg: "bg-green-50 dark:bg-green-900/10", label: "✅ All Clear", color: "text-green-600" },
};

export function AlertDashboard({ active, resolved, criticalCount, status, bySeverity, byService }: AlertDashboardProps) {
  const s = STATUS_STYLES[status] ?? STATUS_STYLES.clear;
  return (
    <div className={`rounded-xl border dark:border-gray-700 overflow-hidden ${s.bg}`}>
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className={`font-semibold ${s.color}`}>{s.label}</h3>
        <span className="text-xs text-gray-400">{active} active · {resolved} resolved</span>
      </div>
      <div className="grid grid-cols-2 divide-x dark:divide-gray-700 p-3 text-xs">
        <div>
          <div className="text-gray-400 mb-1">By Severity</div>
          {Object.entries(bySeverity).map(([sev, c]) => (
            <div key={sev} className="flex justify-between py-0.5"><span className="capitalize">{sev}</span><span>{c}</span></div>
          ))}
        </div>
        <div className="pl-3">
          <div className="text-gray-400 mb-1">By Service</div>
          {Object.entries(byService).map(([svc, c]) => (
            <div key={svc} className="flex justify-between py-0.5"><span>{svc}</span><span>{c}</span></div>
          ))}
        </div>
      </div>
    </div>
  );
}
