"use client";

interface Component { name: string; status: string; }
interface StatusPageDisplayProps { appName: string; overallStatus: string; components: Component[]; lastUpdated: string; }

const statusStyles: Record<string, { color: string; label: string; icon: string }> = {
  operational: { color: "text-green-600", label: "Operational", icon: "🟢" },
  degraded: { color: "text-yellow-600", label: "Degraded", icon: "🟡" },
  partial_outage: { color: "text-orange-600", label: "Partial Outage", icon: "🟠" },
  major_outage: { color: "text-red-600", label: "Major Outage", icon: "🔴" },
};

export function StatusPageDisplay({ appName, overallStatus, components, lastUpdated }: StatusPageDisplayProps) {
  const overall = statusStyles[overallStatus] ?? statusStyles.operational;
  return (
    <div className="space-y-4">
      <div className={`rounded-lg p-4 text-center ${overallStatus === "operational" ? "bg-green-50 dark:bg-green-900/10" : "bg-red-50 dark:bg-red-900/10"}`}>
        <h1 className="text-xl font-bold">{appName}</h1>
        <p className={`mt-1 text-lg font-semibold ${overall.color}`}>{overall.icon} {overall.label}</p>
      </div>
      <div className="space-y-2">
        {components.map(c => {
          const s = statusStyles[c.status] ?? statusStyles.operational;
          return (
            <div key={c.name} className="flex items-center justify-between rounded border px-4 py-2.5 dark:border-gray-700">
              <span className="font-medium">{c.name}</span>
              <span className={`text-sm ${s.color}`}>{s.icon} {s.label}</span>
            </div>
          );
        })}
      </div>
      <p className="text-center text-xs text-gray-400">Last updated: {new Date(lastUpdated).toLocaleString()}</p>
    </div>
  );
}
