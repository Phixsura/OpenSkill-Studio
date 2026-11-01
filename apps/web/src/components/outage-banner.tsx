"use client";

interface OutageBannerProps { overallStatus: string; activeIncidents: number;
  affectedServices: string[]; latestMessage: string; }

const STATUS_STYLES: Record<string, { bg: string; icon: string; label: string }> = {
  operational: { bg: "bg-green-50 dark:bg-green-900/10", icon: "✅", label: "All Systems Operational" },
  degraded: { bg: "bg-yellow-50 dark:bg-yellow-900/10", icon: "⚠️", label: "Partial System Outage" },
  major_outage: { bg: "bg-red-50 dark:bg-red-900/10", icon: "🔴", label: "Major System Outage" },
};

export function OutageBanner({ overallStatus, activeIncidents, affectedServices, latestMessage }: OutageBannerProps) {
  const s = STATUS_STYLES[overallStatus] ?? STATUS_STYLES.operational;
  return (
    <div className={`rounded-xl border dark:border-gray-700 overflow-hidden ${s.bg}`}>
      <div className="p-4">
        <div className="flex items-center gap-2">
          <span className="text-lg">{s.icon}</span>
          <h3 className="font-semibold text-sm">{s.label}</h3>
        </div>
        {activeIncidents > 0 && (
          <div className="mt-2 text-xs">
            <div className="text-gray-600">{activeIncidents} active incident(s) · affected: {affectedServices.join(", ")}</div>
            <div className="text-gray-500 mt-1">{latestMessage}</div>
          </div>
        )}
      </div>
    </div>
  );
}
