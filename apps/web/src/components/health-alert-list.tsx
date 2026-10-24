"use client";

interface Alert {
  rule: string;
  severity: string;
  metric: string;
  value: number;
  threshold: number;
  message: string;
}

interface HealthAlertListProps {
  alerts: Alert[];
}

const SEVERITY_STYLES: Record<string, { bg: string; icon: string }> = {
  critical: { bg: "bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800", icon: "🚨" },
  warning: { bg: "bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800", icon: "⚠️" },
  info: { bg: "bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800", icon: "ℹ️" },
};

export function HealthAlertList({ alerts }: HealthAlertListProps) {
  if (alerts.length === 0) {
    return <p className="py-3 text-center text-sm text-green-600 dark:text-green-400">✅ No active alerts</p>;
  }

  const sorted = [...alerts].sort((a, b) => {
    const order: Record<string, number> = { critical: 0, warning: 1, info: 2 };
    return (order[a.severity] ?? 3) - (order[b.severity] ?? 3);
  });

  return (
    <div className="space-y-2">
      {sorted.map((alert, i) => {
        const style = SEVERITY_STYLES[alert.severity] ?? SEVERITY_STYLES.info;
        return (
          <div key={i} className={`rounded-lg border p-3 ${style.bg}`}>
            <div className="flex items-center gap-2 text-sm">
              <span>{style.icon}</span>
              <span className="font-medium">{alert.rule.replace(/_/g, " ")}</span>
              <span className="ml-auto text-xs text-gray-500">{alert.metric}: {alert.value}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
