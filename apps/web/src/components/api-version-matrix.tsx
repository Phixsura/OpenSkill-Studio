"use client";

interface ApiVersion { version: string; status: string; sunset_date?: string; created_at?: string; }
interface ApiVersionMatrixProps { versions: ApiVersion[]; latestVersion: string | null;
  onDeprecate: (version: string) => void; }

const statusStyle: Record<string, { bg: string; label: string }> = {
  active: { bg: "bg-green-100 text-green-700 dark:bg-green-900/30", label: "Active" },
  deprecated: { bg: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", label: "Deprecated" },
  sunset: { bg: "bg-red-100 text-red-700 dark:bg-red-900/30", label: "Sunset" },
};

export function ApiVersionMatrix({ versions, latestVersion, onDeprecate }: ApiVersionMatrixProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">API Versions</h2>
        {latestVersion && <span className="text-sm text-gray-400">Latest: {latestVersion}</span>}
      </div>
      <div className="space-y-2">
        {versions.map(v => {
          const s = statusStyle[v.status] ?? statusStyle.active;
          return (
            <div key={v.version} className="flex items-center justify-between rounded-lg border p-3 dark:border-gray-700">
              <div className="flex items-center gap-2">
                <span className="font-mono text-lg font-bold">{v.version}</span>
                <span className={`rounded-full px-2 py-0.5 text-xs ${s.bg}`}>{s.label}</span>
              </div>
              <div className="flex items-center gap-2">
                {v.sunset_date && <span className="text-xs text-gray-400">Sunset: {v.sunset_date.slice(0, 10)}</span>}
                {v.status === "active" && v.version !== latestVersion && (
                  <button onClick={() => onDeprecate(v.version)} className="text-xs text-yellow-600">Deprecate</button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
