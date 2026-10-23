"use client";

interface CostAlert { level: string; message: string; }
interface CostAlertBannerProps { currentSpend: number; budget: number; pctUsed: number;
  projectedSpend: number; alerts: CostAlert[]; status: string; onManage: () => void; }

const statusStyle: Record<string, { bg: string; icon: string }> = {
  ok: { bg: "bg-green-50 border-green-200 dark:bg-green-900/10 dark:border-green-800", icon: "✅" },
  warning: { bg: "bg-yellow-50 border-yellow-200 dark:bg-yellow-900/10 dark:border-yellow-800", icon: "⚠️" },
  critical: { bg: "bg-red-50 border-red-200 dark:bg-red-900/10 dark:border-red-800", icon: "🚨" },
};

export function CostAlertBanner({ currentSpend, budget, pctUsed, projectedSpend, alerts, status, onManage }: CostAlertBannerProps) {
  const s = statusStyle[status] ?? statusStyle.ok;
  return (
    <div className={`space-y-3 rounded-lg border p-4 ${s.bg}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">{s.icon}</span>
          <h3 className="font-semibold">Cost Monitor</h3>
        </div>
        <button onClick={onManage} className="text-xs text-blue-500">Manage Budget</button>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-sm">
        <div><p className="font-bold">${currentSpend.toFixed(2)}</p><p className="text-xs text-gray-400">Spent</p></div>
        <div><p className="font-bold">${budget.toFixed(2)}</p><p className="text-xs text-gray-400">Budget</p></div>
        <div><p className="font-bold">{pctUsed}%</p><p className="text-xs text-gray-400">Used</p></div>
      </div>
      <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-full rounded-full ${status === "critical" ? "bg-red-500" : status === "warning" ? "bg-yellow-500" : "bg-green-500"}`}
          style={{ width: `${Math.min(pctUsed, 100)}%` }} />
      </div>
      {alerts.map((a, i) => (
        <p key={i} className={`text-xs ${a.level === "critical" ? "text-red-600" : "text-yellow-600"}`}>
          {a.message}
        </p>
      ))}
    </div>
  );
}
