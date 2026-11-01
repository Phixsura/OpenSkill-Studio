"use client";

interface SystemComponent {
  name: string;
  status: "operational" | "degraded" | "partial_outage" | "major_outage";
}

interface Incident {
  id: string;
  title: string;
  status: "investigating" | "identified" | "monitoring" | "resolved";
  severity: "minor" | "major" | "critical";
  createdAt: string;
  updatedAt: string;
  updates: { message: string; timestamp: string }[];
}

export function ExtensionStatusPage({
  extensionName,
  components,
  incidents,
  overallUptime,
}: {
  extensionName: string;
  components: SystemComponent[];
  incidents: Incident[];
  overallUptime: number;
}) {
  const statusColors: Record<string, { bg: string; text: string }> = {
    operational: { bg: "bg-green-500", text: "text-green-600 dark:text-green-400" },
    degraded: { bg: "bg-yellow-500", text: "text-yellow-600 dark:text-yellow-400" },
    partial_outage: { bg: "bg-orange-500", text: "text-orange-600 dark:text-orange-400" },
    major_outage: { bg: "bg-red-500", text: "text-red-600 dark:text-red-400" },
  };

  const incidentIcons: Record<string, string> = {
    investigating: "🔍", identified: "🎯", monitoring: "👀", resolved: "✅",
  };

  const allOperational = components.every((c) => c.status === "operational");
  const activeIncidents = incidents.filter((i) => i.status !== "resolved");

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      {/* Overall status */}
      <div className={`rounded-xl p-6 text-center ${
        allOperational ? "bg-green-50 dark:bg-green-900/10" : "bg-yellow-50 dark:bg-yellow-900/10"
      }`}>
        <div className="text-3xl mb-2">{allOperational ? "✅" : "⚠️"}</div>
        <h1 className="text-xl font-bold">{extensionName} Status</h1>
        <p className={`text-sm ${allOperational ? "text-green-600" : "text-yellow-600"}`}>
          {allOperational ? "All Systems Operational" : `${activeIncidents.length} Active Incident(s)`}
        </p>
        <p className="text-xs text-gray-400 mt-1">Uptime: {overallUptime}%</p>
      </div>

      {/* Components */}
      <div className="rounded-xl border dark:border-gray-700 p-4">
        <h2 className="font-semibold text-sm mb-3">System Components</h2>
        <div className="space-y-2">
          {components.map((comp) => {
            const cfg = statusColors[comp.status];
            return (
              <div key={comp.name} className="flex items-center justify-between py-1">
                <span className="text-sm">{comp.name}</span>
                <div className="flex items-center gap-2">
                  <div className={`w-2.5 h-2.5 rounded-full ${cfg.bg}`} />
                  <span className={`text-xs ${cfg.text}`}>{comp.status.replace("_", " ")}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Incidents */}
      {incidents.length > 0 && (
        <div className="space-y-3">
          <h2 className="font-semibold text-sm">Recent Incidents</h2>
          {incidents.map((inc) => (
            <div key={inc.id} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span>{incidentIcons[inc.status]}</span>
                  <span className="font-medium text-sm">{inc.title}</span>
                </div>
                <span className="text-xs text-gray-400">{inc.createdAt}</span>
              </div>
              {inc.updates.slice(0, 3).map((u, i) => (
                <div key={i} className="ml-7 text-xs text-gray-500 py-0.5 border-l-2 border-gray-200 dark:border-gray-700 pl-3">
                  <span className="text-gray-400">{u.timestamp}</span> — {u.message}
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
