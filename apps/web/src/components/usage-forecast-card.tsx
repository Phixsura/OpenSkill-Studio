"use client";

interface UsageForecastCardProps { resource: string; currentUsage: number; limit: number;
  daysUntilBreach: number; urgency: string; dailyGrowth: number; onUpgrade: () => void; }

const urgencyStyle: Record<string, { color: string; label: string }> = {
  ok: { color: "text-green-600", label: "On track" },
  warning: { color: "text-yellow-600", label: "Approaching limit" },
  critical: { color: "text-red-600", label: "Limit imminent" },
};

export function UsageForecastCard({ resource, currentUsage, limit, daysUntilBreach, urgency, dailyGrowth, onUpgrade }: UsageForecastCardProps) {
  const pct = Math.round((currentUsage / Math.max(limit, 1)) * 100);
  const u = urgencyStyle[urgency] ?? urgencyStyle.ok;
  return (
    <div className="rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold capitalize">{resource.replace(/_/g, " ")}</h3>
        <span className={`text-xs font-medium ${u.color}`}>{u.label}</span>
      </div>
      <div className="mt-2">
        <div className="flex justify-between text-xs text-gray-400">
          <span>{currentUsage.toLocaleString()} / {limit.toLocaleString()}</span>
          <span>{pct}%</span>
        </div>
        <div className="mt-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
          <div className={`h-full rounded-full ${urgency === "critical" ? "bg-red-500" : urgency === "warning" ? "bg-yellow-500" : "bg-green-500"}`}
            style={{ width: `${Math.min(pct, 100)}%` }} />
        </div>
      </div>
      <div className="mt-2 flex items-center justify-between text-xs text-gray-400">
        <span>+{dailyGrowth}/day</span>
        <span>{daysUntilBreach > 0 ? `~${daysUntilBreach} days left` : "Limit reached"}</span>
      </div>
      {urgency !== "ok" && (
        <button onClick={onUpgrade} className="mt-2 w-full rounded bg-blue-600 py-1.5 text-xs text-white">Upgrade</button>
      )}
    </div>
  );
}
