"use client";

interface ConfigVersionInfo {
  version: number;
  changed_by: string;
  timestamp: string;
  key_count: number;
}

interface RuntimeConfigCardProps {
  currentValues: Record<string, unknown>;
  history: ConfigVersionInfo[];
  appName: string;
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

export default function RuntimeConfigCard({
  currentValues,
  history,
  appName,
}: RuntimeConfigCardProps) {
  const keys = Object.keys(currentValues).sort();
  const currentVersion = history.length > 0 ? history[0].version : 0;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Runtime Config</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-[10px] text-gray-600 dark:bg-gray-800 dark:text-gray-400">
            v{currentVersion}
          </span>
          <span className="text-xs text-gray-400">{keys.length} keys</span>
        </div>
      </div>

      {/* Current values */}
      {keys.length > 0 && (
        <div className="mb-3 rounded-lg bg-gray-50 p-3 dark:bg-gray-800/50">
          <div className="space-y-0.5">
            {keys.map((k) => (
              <div key={k} className="flex items-center justify-between font-mono text-[11px]">
                <span className="text-gray-600 dark:text-gray-400">{k}</span>
                <span className="text-gray-800 dark:text-gray-200">
                  {JSON.stringify(currentValues[k])}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Version history */}
      {history.length > 0 && (
        <div>
          <p className="mb-1.5 text-xs font-medium text-gray-500">History</p>
          <div className="space-y-1">
            {history.slice(0, 5).map((v) => (
              <div key={v.version} className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-gray-500">v{v.version}</span>
                  <span className="text-gray-600 dark:text-gray-400">{v.changed_by}</span>
                </div>
                <span className="text-gray-400">{timeAgo(v.timestamp)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {keys.length === 0 && history.length === 0 && (
        <p className="text-center text-sm text-gray-400">No configuration</p>
      )}
    </div>
  );
}
