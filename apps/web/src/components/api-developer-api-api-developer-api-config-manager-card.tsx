"use client";

interface Props { config: Record<string, unknown>; version: number; historyCount: number; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiConfigManagerCard({ config, version, historyCount, appName }: Props) {
  const entries = Object.entries(config);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚙️ Config Manager</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right text-[10px] text-gray-400">
          <p>v{version}</p>
          <p>{historyCount} snapshots</p>
        </div>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No config values</p>
      ) : (
        <div className="space-y-1">
          {entries.map(([k, v]) => (
            <div key={k} className="flex items-center justify-between text-[11px]">
              <span className="font-mono text-gray-700 dark:text-gray-300">{k}</span>
              <span className="font-mono text-gray-400">{String(v)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
