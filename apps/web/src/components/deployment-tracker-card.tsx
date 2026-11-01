"use client";

interface DeploymentInfo {
  deployment_id: string;
  environment: string;
  version: string;
  status: "pending" | "deploying" | "deployed" | "rolled_back" | "failed";
  created_at: string;
  error_message: string | null;
  rolled_back_to: string | null;
}

interface DeploymentTrackerCardProps {
  deployments: DeploymentInfo[];
  appName: string;
  environments: string[];
}

const STATUS_STYLES: Record<string, { label: string; bg: string; text: string; icon: string }> = {
  pending: {
    label: "Pending",
    bg: "bg-gray-100 dark:bg-gray-800",
    text: "text-gray-600 dark:text-gray-400",
    icon: "⏳",
  },
  deploying: {
    label: "Deploying",
    bg: "bg-blue-100 dark:bg-blue-900/30",
    text: "text-blue-700 dark:text-blue-400",
    icon: "🚀",
  },
  deployed: {
    label: "Deployed",
    bg: "bg-green-100 dark:bg-green-900/30",
    text: "text-green-700 dark:text-green-400",
    icon: "✅",
  },
  rolled_back: {
    label: "Rolled Back",
    bg: "bg-yellow-100 dark:bg-yellow-900/30",
    text: "text-yellow-700 dark:text-yellow-400",
    icon: "⏪",
  },
  failed: {
    label: "Failed",
    bg: "bg-red-100 dark:bg-red-900/30",
    text: "text-red-700 dark:text-red-400",
    icon: "❌",
  },
};

function StatusBadge({ status }: { status: string }) {
  const st = STATUS_STYLES[status] ?? STATUS_STYLES.pending;
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${st.bg} ${st.text}`}
    >
      <span>{st.icon}</span>
      {st.label}
    </span>
  );
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 60_000) return "just now";
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

function EnvironmentRow({ env, deployments }: { env: string; deployments: DeploymentInfo[] }) {
  const envDeps = deployments
    .filter((d) => d.environment === env)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  const latest = envDeps[0] ?? null;

  return (
    <div className="flex items-center justify-between py-2.5">
      <div className="flex items-center gap-2">
        <span className="w-20 text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
          {env}
        </span>
        {latest ? (
          <>
            <span className="font-mono text-sm text-gray-800 dark:text-gray-200">
              {latest.version}
            </span>
            <StatusBadge status={latest.status} />
          </>
        ) : (
          <span className="text-xs text-gray-400">No deployments</span>
        )}
      </div>
      {latest && <span className="text-[11px] text-gray-400">{timeAgo(latest.created_at)}</span>}
    </div>
  );
}

export default function DeploymentTrackerCard({
  deployments,
  appName,
  environments,
}: DeploymentTrackerCardProps) {
  const failedCount = deployments.filter((d) => d.status === "failed").length;
  const activeCount = deployments.filter(
    (d) => d.status === "deploying" || d.status === "pending",
  ).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Deployments</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex gap-2">
          {activeCount > 0 && (
            <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
              {activeCount} in progress
            </span>
          )}
          {failedCount > 0 && (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              {failedCount} failed
            </span>
          )}
        </div>
      </div>

      {/* Environment rows */}
      <div className="divide-y divide-gray-100 dark:divide-gray-800">
        {environments.map((env) => (
          <EnvironmentRow key={env} env={env} deployments={deployments} />
        ))}
      </div>

      {/* Recent history */}
      {deployments.length > 0 && (
        <div className="mt-4 border-t border-gray-100 pt-3 dark:border-gray-800">
          <p className="mb-2 text-xs font-medium text-gray-500 dark:text-gray-400">
            Recent Activity
          </p>
          <ul className="space-y-1.5">
            {deployments
              .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
              .slice(0, 5)
              .map((d) => (
                <li key={d.deployment_id} className="flex items-center gap-2 text-xs">
                  <StatusBadge status={d.status} />
                  <span className="font-mono text-gray-700 dark:text-gray-300">{d.version}</span>
                  <span className="text-gray-400">→ {d.environment}</span>
                  {d.status === "rolled_back" && d.rolled_back_to && (
                    <span className="text-yellow-600 dark:text-yellow-400">
                      → {d.rolled_back_to}
                    </span>
                  )}
                  {d.status === "failed" && d.error_message && (
                    <span className="truncate text-red-500" title={d.error_message}>
                      {d.error_message}
                    </span>
                  )}
                </li>
              ))}
          </ul>
        </div>
      )}
    </div>
  );
}
