"use client";

interface UsageAlert { resource: string; pct: number; severity: string; message: string; }
interface UsageLimitAlertsProps { alerts: UsageAlert[]; hasCritical: boolean; }

const sevStyles: Record<string, string> = {
  critical: "border-red-300 bg-red-50 dark:bg-red-900/10 dark:border-red-700",
  warning: "border-yellow-300 bg-yellow-50 dark:bg-yellow-900/10 dark:border-yellow-700",
};

export function UsageLimitAlerts({ alerts, hasCritical }: UsageLimitAlertsProps) {
  if (alerts.length === 0) return null;
  return (
    <div className="space-y-2">
      {alerts.map((a, i) => (
        <div key={i} className={`rounded-lg border p-3 ${sevStyles[a.severity] ?? ""}`}>
          <div className="flex items-center gap-2">
            <span>{a.severity === "critical" ? "🚨" : "⚠️"}</span>
            <p className="text-sm font-medium">{a.message}</p>
          </div>
          <div className="mt-2 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
            <div className={`h-full rounded-full ${a.severity === "critical" ? "bg-red-500" : "bg-yellow-500"}`}
              style={{ width: `${Math.min(a.pct, 100)}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}
