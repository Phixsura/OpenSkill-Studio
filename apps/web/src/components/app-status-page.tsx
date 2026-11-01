"use client";

interface StatusComponent {
  name: string;
  status: "operational" | "degraded" | "partial_outage" | "major_outage" | "maintenance";
  uptime_pct: number;
}

interface ActiveIncident {
  title: string;
  status: string;
  severity: string;
  last_update: string;
}

interface MaintenanceWindow {
  title: string;
  scheduled_start: string;
  scheduled_end: string;
  description: string;
}

interface StatusPageData {
  app_name: string;
  system_status: "all_operational" | "minor_issues" | "major_issues" | "outage";
  components: StatusComponent[];
  active_incidents: ActiveIncident[];
  maintenance_windows: MaintenanceWindow[];
}

interface AppStatusPageProps {
  page: StatusPageData;
}

const SYSTEM_STYLES: Record<string, { label: string; color: string; bg: string }> = {
  all_operational: {
    label: "All Systems Operational",
    color: "text-green-700",
    bg: "bg-green-100 dark:bg-green-900/20 dark:text-green-300",
  },
  minor_issues: {
    label: "Minor System Issues",
    color: "text-yellow-700",
    bg: "bg-yellow-100 dark:bg-yellow-900/20 dark:text-yellow-300",
  },
  major_issues: {
    label: "Major System Issues",
    color: "text-orange-700",
    bg: "bg-orange-100 dark:bg-orange-900/20 dark:text-orange-300",
  },
  outage: {
    label: "System Outage",
    color: "text-red-700",
    bg: "bg-red-100 dark:bg-red-900/20 dark:text-red-300",
  },
};

const COMP_STYLES: Record<string, { label: string; dot: string }> = {
  operational: { label: "Operational", dot: "bg-green-500" },
  degraded: { label: "Degraded", dot: "bg-yellow-500" },
  partial_outage: { label: "Partial Outage", dot: "bg-orange-500" },
  major_outage: { label: "Major Outage", dot: "bg-red-500" },
  maintenance: { label: "Maintenance", dot: "bg-blue-500" },
};

export function AppStatusPage({ page }: AppStatusPageProps) {
  const sys = SYSTEM_STYLES[page.system_status] ?? SYSTEM_STYLES.all_operational;

  return (
    <div className="space-y-4">
      {/* System banner */}
      <div className={`rounded-lg px-4 py-3 text-center font-semibold ${sys.bg} ${sys.color}`}>
        {sys.label}
      </div>

      {/* Components */}
      <div className="rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="border-b border-gray-200 px-4 py-2.5 dark:border-gray-700">
          <h3 className="text-sm font-semibold">Components</h3>
        </div>
        <div className="divide-y divide-gray-100 dark:divide-gray-800">
          {page.components.map((c) => {
            const cs = COMP_STYLES[c.status] ?? COMP_STYLES.operational;
            return (
              <div key={c.name} className="flex items-center justify-between px-4 py-2.5">
                <span className="text-sm">{c.name}</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">{c.uptime_pct}%</span>
                  <span className={`h-2.5 w-2.5 rounded-full ${cs.dot}`} />
                  <span className="text-xs text-gray-500">{cs.label}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Incidents */}
      {page.active_incidents.length > 0 && (
        <div className="rounded-lg border border-red-200 dark:border-red-800">
          <div className="border-b border-red-200 px-4 py-2.5 dark:border-red-800">
            <h3 className="text-sm font-semibold text-red-700 dark:text-red-400">
              Active Incidents
            </h3>
          </div>
          {page.active_incidents.map((inc, i) => (
            <div key={i} className="px-4 py-2.5">
              <p className="text-sm font-medium">{inc.title}</p>
              <p className="text-xs text-gray-500">{inc.last_update}</p>
            </div>
          ))}
        </div>
      )}

      {/* Maintenance */}
      {page.maintenance_windows.length > 0 && (
        <div className="rounded-lg border border-blue-200 dark:border-blue-800">
          <div className="border-b border-blue-200 px-4 py-2.5 dark:border-blue-800">
            <h3 className="text-sm font-semibold text-blue-700 dark:text-blue-400">
              Scheduled Maintenance
            </h3>
          </div>
          {page.maintenance_windows.map((m, i) => (
            <div key={i} className="px-4 py-2.5">
              <p className="text-sm font-medium">{m.title}</p>
              <p className="text-xs text-gray-500">{m.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
