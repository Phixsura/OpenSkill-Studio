"use client";

interface StatusComponentInfo {
  component_id: string;
  name: string;
  status: "operational" | "degraded" | "partial_outage" | "major_outage";
}

interface StatusIncidentInfo {
  incident_id: string;
  title: string;
  status: string;
}

interface StatusPageCardProps {
  components: StatusComponentInfo[];
  incidents: StatusIncidentInfo[];
  overallStatus: string;
  appName: string;
}

const statusDot: Record<string, string> = {
  operational: "bg-green-500",
  degraded: "bg-yellow-500",
  partial_outage: "bg-orange-500",
  major_outage: "bg-red-500",
};

const overallBanner: Record<string, string> = {
  operational: "bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300",
  degraded: "bg-yellow-50 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300",
  partial_outage: "bg-orange-50 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300",
  major_outage: "bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-300",
};

export default function StatusPageCard({
  components,
  incidents,
  overallStatus,
  appName,
}: StatusPageCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚦 Status Page</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{components.length} components</span>
      </div>

      <div
        className={`mb-3 rounded-lg px-3 py-1.5 text-center text-xs font-medium ${overallBanner[overallStatus] ?? ""}`}
      >
        {overallStatus.replace("_", " ")}
      </div>

      {incidents.length > 0 && (
        <div className="mb-3 space-y-1">
          {incidents.map((i) => (
            <div
              key={i.incident_id}
              className="rounded bg-red-50 px-3 py-1 text-xs text-red-700 dark:bg-red-900/20 dark:text-red-300"
            >
              ⚠ {i.title} — {i.status}
            </div>
          ))}
        </div>
      )}

      <div className="space-y-1">
        {components.map((c) => (
          <div key={c.component_id} className="flex items-center justify-between text-[11px]">
            <div className="flex items-center gap-2">
              <span className={`h-2 w-2 rounded-full ${statusDot[c.status]}`} />
              <span className="text-gray-700 dark:text-gray-300">{c.name}</span>
            </div>
            <span className="text-gray-400">{c.status.replace("_", " ")}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
