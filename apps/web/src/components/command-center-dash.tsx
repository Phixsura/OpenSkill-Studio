"use client";

interface CommandCenterDashProps { score: number; status: string;
  services: { total: number; healthyPct: number; unhealthy: number };
  deployments: { successRate: number; failed: number };
  alerts: { total: number; critical: number };
  actionItems: string[]; }

const STATUS_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  green: { bg: "bg-green-500", text: "text-green-600", label: "All Systems Go" },
  yellow: { bg: "bg-yellow-500", text: "text-yellow-600", label: "Degraded" },
  red: { bg: "bg-red-500", text: "text-red-600", label: "Critical" },
};

export function CommandCenterDash({ score, status, services, deployments, alerts, actionItems }: CommandCenterDashProps) {
  const s = STATUS_STYLES[status] ?? STATUS_STYLES.green;
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-6 text-center ${status === "green" ? "bg-green-50 dark:bg-green-900/10" : status === "red" ? "bg-red-50 dark:bg-red-900/10" : "bg-yellow-50 dark:bg-yellow-900/10"}`}>
        <div className={`text-4xl font-bold ${s.text}`}>{score}</div>
        <div className="text-sm text-gray-500 mt-1">{s.label}</div>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold">{services.healthyPct}%</div>
          <div className="text-[10px] text-gray-400">Services</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold">{deployments.successRate}%</div>
          <div className="text-[10px] text-gray-400">Deploys</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className={`text-lg font-bold ${alerts.critical > 0 ? "text-red-600" : ""}`}>{alerts.critical}</div>
          <div className="text-[10px] text-gray-400">Critical</div>
        </div>
      </div>
      {actionItems.length > 0 && (
        <div className="p-3">
          {actionItems.map((a, i) => <div key={i} className="text-xs py-0.5">⚠ {a}</div>)}
        </div>
      )}
    </div>
  );
}
