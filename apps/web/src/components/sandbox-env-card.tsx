"use client";

interface SandboxInfo {
  sandbox_id: string;
  app_version: string;
  status: "creating" | "running" | "stopped" | "terminated" | "error";
  memory_limit_mb: number;
  memory_used_mb: number;
  cpu_used_seconds: number;
  created_at: string;
  exit_code: number | null;
  log_lines: number;
}

interface SandboxEnvCardProps {
  sandboxes: SandboxInfo[];
  appName: string;
}

const STATUS_STYLES: Record<string, { icon: string; text: string; bg: string }> = {
  creating: {
    icon: "🔧",
    text: "text-blue-600 dark:text-blue-400",
    bg: "bg-blue-100 dark:bg-blue-900/30",
  },
  running: {
    icon: "▶️",
    text: "text-green-600 dark:text-green-400",
    bg: "bg-green-100 dark:bg-green-900/30",
  },
  stopped: {
    icon: "⏹️",
    text: "text-gray-600 dark:text-gray-400",
    bg: "bg-gray-100 dark:bg-gray-800",
  },
  terminated: {
    icon: "⛔",
    text: "text-red-600 dark:text-red-400",
    bg: "bg-red-100 dark:bg-red-900/30",
  },
  error: {
    icon: "❌",
    text: "text-red-600 dark:text-red-400",
    bg: "bg-red-100 dark:bg-red-900/30",
  },
};

function MemoryBar({ used, limit }: { used: number; limit: number }) {
  const pct = limit > 0 ? Math.min((used / limit) * 100, 100) : 0;
  const color = pct >= 90 ? "bg-red-500" : pct >= 70 ? "bg-yellow-500" : "bg-green-500";
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-16 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-1.5 rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[11px] text-gray-500">
        {used.toFixed(0)}/{limit}MB
      </span>
    </div>
  );
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 60_000) return "just now";
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

export default function SandboxEnvCard({ sandboxes, appName }: SandboxEnvCardProps) {
  const runningCount = sandboxes.filter((s) => s.status === "running").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Sandboxes</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span
          className={`rounded-full px-2 py-0.5 text-xs font-medium ${
            runningCount > 0
              ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
              : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"
          }`}
        >
          {runningCount} running
        </span>
      </div>

      {sandboxes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No sandboxes</p>
      ) : (
        <div className="space-y-2.5">
          {sandboxes.map((sb) => {
            const st = STATUS_STYLES[sb.status] ?? STATUS_STYLES.error;
            return (
              <div
                key={sb.sandbox_id}
                className="rounded-lg border border-gray-100 px-3 py-2.5 dark:border-gray-800"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span>{st.icon}</span>
                    <span className="font-mono text-sm text-gray-800 dark:text-gray-200">
                      {sb.sandbox_id}
                    </span>
                    <span
                      className={`rounded px-1.5 py-0.5 text-[10px] font-medium capitalize ${st.bg} ${st.text}`}
                    >
                      {sb.status}
                    </span>
                  </div>
                  <span className="text-xs text-gray-400">v{sb.app_version}</span>
                </div>
                <div className="mt-1.5 flex items-center justify-between">
                  <MemoryBar used={sb.memory_used_mb} limit={sb.memory_limit_mb} />
                  <div className="flex items-center gap-3 text-[11px] text-gray-400">
                    <span>CPU: {sb.cpu_used_seconds.toFixed(1)}s</span>
                    <span>{sb.log_lines} log lines</span>
                  </div>
                </div>
                <div className="mt-1 flex items-center justify-between text-[11px] text-gray-400">
                  <span>Created {timeAgo(sb.created_at)}</span>
                  {sb.exit_code !== null && (
                    <span className={sb.exit_code === 0 ? "text-green-500" : "text-red-500"}>
                      Exit: {sb.exit_code}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
