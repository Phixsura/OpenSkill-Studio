"use client";

interface DeveloperStats {
  extensionsPublished: number;
  totalDownloads: number;
  activeInstalls: number;
  avgRating: number;
  apiCallsToday: number;
  apiQuotaUsed: number;
  webhookDeliveries: number;
  webhookFailures: number;
}

interface RecentActivity {
  id: string;
  type: "install" | "review" | "update" | "webhook";
  message: string;
  timestamp: string;
}

export function DeveloperPortalDashboard({
  stats,
  activities,
}: {
  stats: DeveloperStats;
  activities: RecentActivity[];
}) {
  const quotaPercent = Math.min(100, Math.round((stats.apiQuotaUsed / 100) * 100));

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">🧑‍💻 Developer Portal</h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Extensions" value={stats.extensionsPublished} icon="📦" />
        <StatCard label="Downloads" value={stats.totalDownloads} icon="⬇️" />
        <StatCard label="Active Installs" value={stats.activeInstalls} icon="✅" />
        <StatCard label="Avg Rating" value={stats.avgRating.toFixed(1)} icon="⭐" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="rounded-xl border dark:border-gray-700 p-4">
          <h3 className="font-semibold mb-3">📊 API Usage</h3>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Calls today</span>
              <span className="font-mono">{stats.apiCallsToday.toLocaleString()}</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${quotaPercent > 80 ? "bg-red-500" : "bg-blue-500"}`}
                style={{ width: `${quotaPercent}%` }}
              />
            </div>
            <div className="text-xs text-gray-500">{quotaPercent}% of daily quota used</div>
          </div>
        </div>

        <div className="rounded-xl border dark:border-gray-700 p-4">
          <h3 className="font-semibold mb-3">🔔 Webhooks</h3>
          <div className="flex gap-6">
            <div>
              <div className="text-2xl font-bold text-green-500">{stats.webhookDeliveries}</div>
              <div className="text-xs text-gray-500">Delivered</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-500">{stats.webhookFailures}</div>
              <div className="text-xs text-gray-500">Failed</div>
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-xl border dark:border-gray-700 p-4">
        <h3 className="font-semibold mb-3">📋 Recent Activity</h3>
        <div className="space-y-2">
          {activities.map((a) => (
            <div key={a.id} className="flex items-center justify-between text-sm py-1 border-b dark:border-gray-800 last:border-0">
              <div className="flex items-center gap-2">
                <TypeBadge type={a.type} />
                <span>{a.message}</span>
              </div>
              <span className="text-xs text-gray-400">{a.timestamp}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon }: { label: string; value: string | number; icon: string }) {
  return (
    <div className="rounded-lg border dark:border-gray-700 p-3 text-center">
      <div className="text-2xl">{icon}</div>
      <div className="text-lg font-bold">{typeof value === "number" ? value.toLocaleString() : value}</div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  );
}

function TypeBadge({ type }: { type: string }) {
  const colors: Record<string, string> = {
    install: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300",
    review: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
    update: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300",
    webhook: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300",
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${colors[type] || "bg-gray-100"}`}>
      {type}
    </span>
  );
}
