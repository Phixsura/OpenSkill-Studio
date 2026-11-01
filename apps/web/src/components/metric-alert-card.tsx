"use client";

interface AlertRuleInfo {
  rule_id: string;
  metric_name: string;
  operator: string;
  threshold: number;
  severity: string;
  state: "ok" | "firing" | "resolved";
  fire_count: number;
}

interface MetricAlertCardProps {
  rules: AlertRuleInfo[];
  appName: string;
}

const stateStyle: Record<string, string> = {
  ok: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  firing: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
  resolved: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
};

const opLabel: Record<string, string> = { gt: ">", lt: "<", gte: "≥", lte: "≤", eq: "=" };

export default function MetricAlertCard({ rules, appName }: MetricAlertCardProps) {
  const firing = rules.filter((r) => r.state === "firing").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🚨 Metric Alerts
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{rules.length} rules</span>
          {firing > 0 && <p className="text-[10px] font-medium text-red-500">{firing} firing</p>}
        </div>
      </div>

      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No alert rules</p>
      ) : (
        <div className="space-y-1.5">
          {rules.map((r) => (
            <div
              key={r.rule_id}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800"
            >
              <div className="flex items-center gap-2">
                <span
                  className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${stateStyle[r.state]}`}
                >
                  {r.state}
                </span>
                <span className="text-xs text-gray-700 dark:text-gray-300">
                  {r.metric_name} {opLabel[r.operator] ?? r.operator} {r.threshold}
                </span>
              </div>
              <span className="text-[10px] text-gray-400">{r.fire_count}x fired</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
