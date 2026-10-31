"use client";

interface UsageAlert { resource: string; usage_pct: number; level: "warning" | "critical"; current: number; limit: number; }
interface UsageAlertBannerProps { alerts: UsageAlert[]; onUpgrade?: () => void; }

export function UsageAlertBanner({ alerts, onUpgrade }: UsageAlertBannerProps) {
  if (alerts.length === 0) return null;
  const hasCritical = alerts.some(a => a.level === "critical");
  return (
    <div className={`rounded-lg border p-4 ${hasCritical ? "border-red-300 bg-red-50 dark:border-red-700 dark:bg-red-900/20" : "border-yellow-300 bg-yellow-50 dark:border-yellow-700 dark:bg-yellow-900/20"}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className={`text-sm font-semibold ${hasCritical ? "text-red-800 dark:text-red-200" : "text-yellow-800 dark:text-yellow-200"}`}>
            {hasCritical ? "🚨 Usage Critical" : "⚠️ Usage Warning"}
          </p>
          <ul className="mt-1 space-y-0.5">
            {alerts.map(a => (
              <li key={a.resource} className="text-xs opacity-80">
                {a.resource}: {a.usage_pct}% used ({a.current.toLocaleString()} / {a.limit.toLocaleString()})
              </li>
            ))}
          </ul>
        </div>
        {onUpgrade && (
          <button onClick={onUpgrade} className="rounded bg-blue-600 px-3 py-1.5 text-xs text-white hover:bg-blue-700">
            Upgrade Plan
          </button>
        )}
      </div>
    </div>
  );
}
