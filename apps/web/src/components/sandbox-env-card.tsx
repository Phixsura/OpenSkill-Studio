"use client";

interface SandboxInfo {
  sandbox_id: string;
  name: string;
  status: "creating" | "running" | "stopped" | "expired";
  cpu_limit: number;
  memory_mb: number;
}

interface SandboxEnvCardProps {
  sandboxes: SandboxInfo[];
  runningCount: number;
  appName: string;
}

const statusStyle: Record<string, string> = {
  creating: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  running: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  stopped: "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
  expired: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function SandboxEnvCard({ sandboxes, runningCount, appName }: SandboxEnvCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏖️ Sandboxes</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {runningCount} running / {sandboxes.length} total
        </span>
      </div>

      {sandboxes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No sandboxes</p>
      ) : (
        <div className="space-y-1.5">
          {sandboxes.map((s) => (
            <div
              key={s.sandbox_id}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-gray-800 dark:text-gray-200">
                  {s.name}
                </span>
                <span
                  className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${statusStyle[s.status]}`}
                >
                  {s.status}
                </span>
              </div>
              <span className="text-[10px] text-gray-400">
                {s.cpu_limit} CPU · {s.memory_mb}MB
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
