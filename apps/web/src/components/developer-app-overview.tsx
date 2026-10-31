"use client";

interface AppStats {
  total_installs: number;
  active_installs: number;
  avg_rating: number;
  total_reviews: number;
  api_calls_today: number;
  api_calls_limit: number;
  webhook_success_rate: number;
  sandbox_executions_today: number;
}

interface AppVersion {
  version: string;
  status: "published" | "pending" | "rejected";
  created_at: string;
}

interface DeveloperAppOverviewProps {
  appId: string;
  appName: string;
  appIcon: string;
  status: "draft" | "published" | "suspended" | "revoked";
  description: string;
  category: string;
  stats: AppStats;
  versions: AppVersion[];
  onPublish: () => void;
  onViewAnalytics: () => void;
  onManageVersions: () => void;
}

const STATUS_BADGE: Record<string, { label: string; color: string }> = {
  draft: { label: "Draft", color: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400" },
  published: {
    label: "Published",
    color: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300",
  },
  suspended: {
    label: "Suspended",
    color: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300",
  },
  revoked: {
    label: "Revoked",
    color: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300",
  },
};

function StatCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="rounded-lg border border-gray-200 p-3 text-center dark:border-gray-700">
      <p className="text-lg font-bold">{value}</p>
      <p className="text-xs text-gray-500">{label}</p>
      {sub && <p className="text-[10px] text-gray-400">{sub}</p>}
    </div>
  );
}

function VersionRow({ v }: { v: AppVersion }) {
  const color =
    v.status === "published"
      ? "text-green-600"
      : v.status === "rejected"
        ? "text-red-600"
        : "text-yellow-600";
  return (
    <div className="flex items-center justify-between py-1.5 text-xs">
      <span className="font-mono font-medium">{v.version}</span>
      <span className={`font-medium ${color}`}>{v.status}</span>
      <span className="text-gray-400">{v.created_at}</span>
    </div>
  );
}

export function DeveloperAppOverview({
  appName,
  appIcon,
  status,
  description,
  category,
  stats,
  versions,
  onPublish,
  onViewAnalytics,
  onManageVersions,
}: DeveloperAppOverviewProps) {
  const badge = STATUS_BADGE[status] ?? STATUS_BADGE.draft;
  const apiPct =
    stats.api_calls_limit > 0
      ? Math.round((stats.api_calls_today / stats.api_calls_limit) * 100)
      : 0;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <span className="text-3xl">{appIcon}</span>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-semibold">{appName}</h2>
              <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${badge.color}`}>
                {badge.label}
              </span>
            </div>
            <p className="text-xs text-gray-500">
              {category} • {description}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          {status === "draft" && (
            <button
              onClick={onPublish}
              className="rounded-md bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700"
            >
              Submit for Review
            </button>
          )}
          <button
            onClick={onViewAnalytics}
            className="rounded-md border border-gray-300 px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-100 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-800"
          >
            Analytics
          </button>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-4 gap-3">
        <StatCard
          label="Active Installs"
          value={stats.active_installs.toLocaleString()}
          sub={`${stats.total_installs.toLocaleString()} total`}
        />
        <StatCard
          label="Rating"
          value={stats.avg_rating.toFixed(1)}
          sub={`${stats.total_reviews} reviews`}
        />
        <StatCard
          label="API Calls Today"
          value={stats.api_calls_today.toLocaleString()}
          sub={`${apiPct}% of limit`}
        />
        <StatCard
          label="Webhook Success"
          value={`${stats.webhook_success_rate}%`}
          sub={`${stats.sandbox_executions_today} sandbox runs`}
        />
      </div>

      {/* API usage bar */}
      <div>
        <div className="flex justify-between text-xs text-gray-500">
          <span>API Usage</span>
          <span>
            {stats.api_calls_today.toLocaleString()} / {stats.api_calls_limit.toLocaleString()}
          </span>
        </div>
        <div className="mt-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
          <div
            className={`h-full rounded-full ${apiPct >= 90 ? "bg-red-500" : apiPct >= 70 ? "bg-yellow-500" : "bg-blue-500"}`}
            style={{ width: `${Math.min(apiPct, 100)}%` }}
          />
        </div>
      </div>

      {/* Versions */}
      <div className="rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between border-b border-gray-200 px-4 py-2.5 dark:border-gray-700">
          <h3 className="text-sm font-semibold">Versions</h3>
          <button
            onClick={onManageVersions}
            className="text-xs text-blue-600 hover:underline dark:text-blue-400"
          >
            Manage
          </button>
        </div>
        <div className="divide-y divide-gray-100 px-4 dark:divide-gray-800">
          {versions.length === 0 ? (
            <p className="py-4 text-center text-xs text-gray-500">No versions yet</p>
          ) : (
            versions.map((v) => <VersionRow key={v.version} v={v} />)
          )}
        </div>
      </div>
    </div>
  );
}
