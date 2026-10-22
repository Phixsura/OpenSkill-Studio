"use client";

interface ServiceStatus { name: string; status: string; uptime_pct: number; }
interface StatusPageWidgetProps { overallStatus: string; services: ServiceStatus[]; }

const STATUS_COLORS: Record<string, string> = {
  operational: "bg-green-500", degraded: "bg-yellow-500", major_outage: "bg-red-500",
};

const OVERALL_LABELS: Record<string, { label: string; color: string }> = {
  all_operational: { label: "All Systems Operational", color: "text-green-600" },
  partial_outage: { label: "Partial System Outage", color: "text-yellow-600" },
  major_outage: { label: "Major System Outage", color: "text-red-600" },
};

export function StatusPageWidget({ overallStatus, services }: StatusPageWidgetProps) {
  const overall = OVERALL_LABELS[overallStatus] || { label: overallStatus, color: "" };
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className={`font-semibold ${overall.color}`}>{overall.label}</h3>
      <ul className="mt-3 space-y-2">
        {services.map(s => (
          <li key={s.name} className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2">
              <span className={`h-2 w-2 rounded-full ${STATUS_COLORS[s.status] || "bg-gray-400"}`} />
              {s.name}
            </span>
            <span className="text-xs text-gray-400">{s.uptime_pct}%</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
