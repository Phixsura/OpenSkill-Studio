"use client";

interface UsageAlertInfo {
  rule_id: string;
  metric: string;
  condition: string;
  threshold: number;
  fired: boolean;
  fire_count: number;
}

interface APIUsageAlertCardProps {
  rules: UsageAlertInfo[];
  appName: string;
}

const condStyle: Record<string, string> = {
  spike: "bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300",
  drop: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  exceeds: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function APIUsageAlertCard({ rules, appName }: APIUsageAlertCardProps) {
  const firing = rules.filter((r) => r.fired).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚠️ Usage Alerts</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{rules.length} rules</span>
          {firing > 0 && <p className="text-[10px] text-red-500">{firing} firing</p>}
        </div>
      </div>

      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No usage alerts</p>
      ) : (
        <div className="space-y-1.5">
          {rules.map((r) => (
            <div key={r.rule_id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${condStyle[r.condition] ?? ""}`}>{r.condition}</span>
                <span className="text-xs text-gray-700 dark:text-gray-300">{r.metric}</span>
              </div>
              <span className="text-[10px] text-gray-400">{r.fire_count}x</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
