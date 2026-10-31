"use client";

interface UsageAlertInfo {
  metric: string;
  level: "ok" | "warning" | "critical";
  used: number;
  limit: number;
  usage_pct: number;
  acknowledged: boolean;
}

interface UsageAlertCardProps {
  alerts: UsageAlertInfo[];
  appName: string;
}

const LEVEL_STYLES: Record<string, { bg: string; text: string; bar: string }> = {
  ok: { bg: "", text: "text-green-600 dark:text-green-400", bar: "bg-green-500" },
  warning: {
    bg: "bg-yellow-50 dark:bg-yellow-950/20",
    text: "text-yellow-600 dark:text-yellow-400",
    bar: "bg-yellow-500",
  },
  critical: {
    bg: "bg-red-50 dark:bg-red-950/20",
    text: "text-red-600 dark:text-red-400",
    bar: "bg-red-500",
  },
};

function formatNum(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export default function UsageAlertCard({ alerts, appName }: UsageAlertCardProps) {
  const activeAlerts = alerts.filter((a) => a.level !== "ok").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Usage Alerts</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {activeAlerts > 0 ? (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            {activeAlerts} alerts
          </span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            All clear
          </span>
        )}
      </div>

      {alerts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No usage metrics monitored</p>
      ) : (
        <div className="space-y-2.5">
          {alerts.map((a) => {
            const st = LEVEL_STYLES[a.level] ?? LEVEL_STYLES.ok;
            return (
              <div
                key={a.metric}
                className={`rounded-lg border border-gray-100 px-3 py-2.5 dark:border-gray-800 ${st.bg}`}
              >
                <div className="mb-1 flex items-center justify-between">
                  <span className="text-sm text-gray-800 dark:text-gray-200">
                    {a.metric.replace(/_/g, " ")}
                  </span>
                  <div className="flex items-center gap-2">
                    {a.acknowledged && <span className="text-[10px] text-gray-400">ack</span>}
                    <span className={`text-xs font-medium uppercase ${st.text}`}>{a.level}</span>
                  </div>
                </div>
                <div className="h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
                  <div
                    className={`h-1.5 rounded-full ${st.bar}`}
                    style={{ width: `${Math.min(a.usage_pct, 100)}%` }}
                  />
                </div>
                <div className="mt-1 flex items-center justify-between text-[11px] text-gray-500">
                  <span>
                    {formatNum(a.used)} / {formatNum(a.limit)}
                  </span>
                  <span>{a.usage_pct}%</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
