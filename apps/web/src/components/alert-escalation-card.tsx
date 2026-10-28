"use client";

interface EscalationAlertInfo {
  alert_id: string;
  current_tier: number;
  tier_name: string;
  acknowledged: boolean;
  acknowledged_by: string;
}

interface EscalationTierInfo {
  tier: number;
  name: string;
  timeout_seconds: number;
}

interface AlertEscalationCardProps {
  alerts: EscalationAlertInfo[];
  tiers: EscalationTierInfo[];
  appName: string;
}

export default function AlertEscalationCard({ alerts, tiers, appName }: AlertEscalationCardProps) {
  const unacked = alerts.filter((a) => !a.acknowledged).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Alert Escalation
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {unacked > 0 ? (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            {unacked} unacked
          </span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            All clear
          </span>
        )}
      </div>

      {/* Tiers */}
      <div className="mb-3 flex gap-1">
        {tiers.map((t) => (
          <span
            key={t.tier}
            className="rounded bg-gray-100 px-2 py-0.5 text-[10px] text-gray-600 dark:bg-gray-800 dark:text-gray-400"
          >
            T{t.tier}: {t.name} ({Math.round(t.timeout_seconds / 60)}m)
          </span>
        ))}
      </div>

      {/* Alerts */}
      {alerts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No active alerts</p>
      ) : (
        <div className="space-y-1.5">
          {alerts.map((a) => (
            <div
              key={a.alert_id}
              className={`flex items-center justify-between rounded px-2.5 py-1.5 ${
                a.acknowledged
                  ? "bg-green-50/50 dark:bg-green-950/10"
                  : "bg-red-50/50 dark:bg-red-950/10"
              }`}
            >
              <div className="flex items-center gap-2">
                <span
                  className={`h-2 w-2 rounded-full ${a.acknowledged ? "bg-green-500" : "animate-pulse bg-red-500"}`}
                />
                <span className="font-mono text-xs text-gray-800 dark:text-gray-200">
                  {a.alert_id}
                </span>
                <span className="text-[10px] text-gray-400">
                  Tier {a.current_tier}: {a.tier_name}
                </span>
              </div>
              {a.acknowledged ? (
                <span className="text-[10px] text-green-600">ack by {a.acknowledged_by}</span>
              ) : (
                <span className="text-[10px] text-red-500">escalating</span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
