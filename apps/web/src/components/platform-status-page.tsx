"use client";

interface ServiceStatus {
  name: string;
  status: "operational" | "degraded" | "outage" | "maintenance";
  uptime: number;
  lastIncident?: string;
}

interface IncidentSummary {
  title: string;
  severity: string;
  status: string;
  timestamp: string;
}

const statusConfig: Record<string, { color: string; icon: string; bg: string }> = {
  operational: { color: "text-green-600", icon: "✅", bg: "bg-green-500" },
  degraded: { color: "text-yellow-600", icon: "⚠️", bg: "bg-yellow-500" },
  outage: { color: "text-red-600", icon: "🔴", bg: "bg-red-500" },
  maintenance: { color: "text-blue-600", icon: "🔧", bg: "bg-blue-500" },
};

export function PlatformStatusPage({
  services,
  incidents,
  overallStatus,
}: {
  services: ServiceStatus[];
  incidents: IncidentSummary[];
  overallStatus: "operational" | "degraded" | "outage";
}) {
  const cfg = statusConfig[overallStatus];

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className={`rounded-xl p-6 text-white text-center ${cfg.bg}`}>
        <span className="text-3xl block mb-1">{cfg.icon}</span>
        <h1 className="text-xl font-bold capitalize">All Systems {overallStatus}</h1>
      </div>

      <div className="space-y-1">
        {services.map((svc) => {
          const sCfg = statusConfig[svc.status];
          return (
            <div key={svc.name} className="rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span>{sCfg.icon}</span>
                <span className="font-medium text-sm">{svc.name}</span>
              </div>
              <div className="flex items-center gap-3 text-xs">
                <span className="text-gray-500">{svc.uptime}% uptime</span>
                <span className={`font-bold capitalize ${sCfg.color}`}>{svc.status}</span>
              </div>
            </div>
          );
        })}
      </div>

      {incidents.length > 0 && (
        <div>
          <h2 className="text-lg font-bold mb-2">Recent Incidents</h2>
          <div className="space-y-2">
            {incidents.map((inc, i) => (
              <div key={i} className="rounded-lg border dark:border-gray-700 p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-sm">{inc.title}</span>
                  <span className="text-xs text-gray-400">{inc.timestamp}</span>
                </div>
                <div className="flex gap-2 text-xs">
                  <span className="text-red-500">{inc.severity}</span>
                  <span className="text-gray-500">{inc.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
