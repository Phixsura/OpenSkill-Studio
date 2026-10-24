"use client";

interface StatusComponent { name: string; status: string; uptimePct: number; }
interface StatusIncident { title: string; status: string; impact: string; updated: string; }
interface PublicStatusPageProps { title: string; overall: string;
  components: StatusComponent[]; activeIncidents: StatusIncident[]; allOperational: boolean; }

const STATUS_COLOR: Record<string, string> = {
  operational: "bg-green-500", degraded: "bg-yellow-500",
  partial_outage: "bg-orange-500", major_outage: "bg-red-500",
};
const STATUS_LABEL: Record<string, string> = {
  operational: "All Systems Operational", degraded: "Degraded Performance",
  partial_outage: "Partial Outage", major_outage: "Major Outage",
};

export function PublicStatusPage({ title, overall, components, activeIncidents, allOperational }: PublicStatusPageProps) {
  return (
    <div className="max-w-2xl mx-auto">
      <div className={`rounded-xl p-6 text-white text-center mb-6 ${overall === "operational" ? "bg-green-600" : overall === "degraded" ? "bg-yellow-600" : "bg-red-600"}`}>
        <h1 className="text-xl font-bold mb-1">{title}</h1>
        <p className="text-sm opacity-90">{STATUS_LABEL[overall] || overall}</p>
      </div>
      <div className="rounded-xl border dark:border-gray-700 mb-6">
        {components.map(c => (
          <div key={c.name} className="flex items-center justify-between px-4 py-3 border-b last:border-0 dark:border-gray-700">
            <span className="text-sm font-medium">{c.name}</span>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">{c.uptimePct}%</span>
              <span className={`w-3 h-3 rounded-full ${STATUS_COLOR[c.status] || "bg-gray-400"}`} />
            </div>
          </div>
        ))}
      </div>
      {activeIncidents.length > 0 && (
        <div className="rounded-xl border border-yellow-200 dark:border-yellow-800 p-4">
          <h3 className="font-semibold mb-2">Active Incidents</h3>
          {activeIncidents.map((inc, i) => (
            <div key={i} className="text-sm mb-2 last:mb-0">
              <p className="font-medium">{inc.title}</p>
              <p className="text-xs text-gray-400">{inc.status} · {inc.impact} impact · {inc.updated}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
