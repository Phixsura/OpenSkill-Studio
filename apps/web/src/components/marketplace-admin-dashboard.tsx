"use client";

interface AdminStats {
  totalExtensions: number;
  pendingReviews: number;
  activeConnectors: number;
  totalDevelopers: number;
  totalRevenue: number;
  openIncidents: number;
  flaggedReviews: number;
  suspendedExtensions: number;
}

interface AdminAlert {
  id: string;
  severity: "info" | "warning" | "critical";
  message: string;
  timestamp: string;
  resolved: boolean;
}

export function MarketplaceAdminDashboard({
  stats,
  alerts,
  onResolveAlert,
}: {
  stats: AdminStats;
  alerts: AdminAlert[];
  onResolveAlert?: (id: string) => void;
}) {
  const unresolved = alerts.filter((a) => !a.resolved);

  const severityColors = {
    info: "border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/10",
    warning: "border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/10",
    critical: "border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/10",
  };

  const severityIcons = { info: "ℹ️", warning: "⚠️", critical: "🚨" };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">🛠️ Marketplace Admin</h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatTile label="Extensions" value={stats.totalExtensions} icon="📦" />
        <StatTile label="Pending Reviews" value={stats.pendingReviews} icon="📋" alert={stats.pendingReviews > 10} />
        <StatTile label="Developers" value={stats.totalDevelopers} icon="👩‍💻" />
        <StatTile label="Revenue" value={`$${(stats.totalRevenue / 100).toLocaleString()}`} icon="💰" />
        <StatTile label="Connectors" value={stats.activeConnectors} icon="🔌" />
        <StatTile label="Incidents" value={stats.openIncidents} icon="🔥" alert={stats.openIncidents > 0} />
        <StatTile label="Flagged Reviews" value={stats.flaggedReviews} icon="🚩" alert={stats.flaggedReviews > 0} />
        <StatTile label="Suspended" value={stats.suspendedExtensions} icon="⛔" alert={stats.suspendedExtensions > 0} />
      </div>

      {unresolved.length > 0 && (
        <div>
          <h3 className="font-semibold mb-3">🔔 Active Alerts ({unresolved.length})</h3>
          <div className="space-y-2">
            {unresolved.map((alert) => (
              <div key={alert.id} className={`flex items-center justify-between rounded-lg border p-3 ${severityColors[alert.severity]}`}>
                <div className="flex items-center gap-2 text-sm">
                  <span>{severityIcons[alert.severity]}</span>
                  <span>{alert.message}</span>
                  <span className="text-xs text-gray-400">{alert.timestamp}</span>
                </div>
                <button
                  onClick={() => onResolveAlert?.(alert.id)}
                  className="text-xs text-gray-500 hover:text-gray-700 px-2 py-1 rounded border"
                >
                  Resolve
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function StatTile({ label, value, icon, alert }: { label: string; value: string | number; icon: string; alert?: boolean }) {
  return (
    <div className={`rounded-lg border dark:border-gray-700 p-3 text-center ${alert ? "border-red-300 dark:border-red-700" : ""}`}>
      <div className="text-xl">{icon}</div>
      <div className={`text-lg font-bold ${alert ? "text-red-600 dark:text-red-400" : ""}`}>
        {typeof value === "number" ? value.toLocaleString() : value}
      </div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  );
}
