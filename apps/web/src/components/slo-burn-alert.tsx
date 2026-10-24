"use client";

interface SloBurnAlertProps { burnRate: number; budgetConsumedPct: number;
  alertLevel: string; timeToExhaustHours: number; critical: boolean; }

const ALERT_STYLES: Record<string, { bg: string; label: string }> = {
  page: { bg: "bg-red-50 dark:bg-red-900/10", label: "🚨 PAGING" },
  ticket: { bg: "bg-yellow-50 dark:bg-yellow-900/10", label: "📋 Ticket" },
  log: { bg: "bg-blue-50 dark:bg-blue-900/10", label: "📝 Log" },
  none: { bg: "", label: "✅ Normal" },
};

export function SloBurnAlert({ burnRate, budgetConsumedPct, alertLevel, timeToExhaustHours, critical }: SloBurnAlertProps) {
  const style = ALERT_STYLES[alertLevel] ?? ALERT_STYLES.none;
  return (
    <div className={`rounded-xl border dark:border-gray-700 overflow-hidden ${style.bg}`}>
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔥 SLO Burn Rate</h3>
        <span className={`text-xs font-medium ${critical ? "text-red-600" : "text-green-600"}`}>{style.label}</span>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700">
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className={`text-xl font-bold ${burnRate > 6 ? "text-red-600" : ""}`}>{burnRate}x</div>
          <div className="text-[9px] text-gray-400">Burn Rate</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-xl font-bold">{budgetConsumedPct}%</div>
          <div className="text-[9px] text-gray-400">Consumed</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-xl font-bold">{timeToExhaustHours}h</div>
          <div className="text-[9px] text-gray-400">Until Exhaust</div>
        </div>
      </div>
    </div>
  );
}
