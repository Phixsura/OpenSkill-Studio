"use client";

interface ApiVersion { version: string; status: string; sunsetDate: string | null; released: string; }
interface ApiVersionSelectorProps { versions: ApiVersion[]; selected: string; onSelect: (v: string) => void; }

const statusBadge: Record<string, string> = {
  stable: "bg-green-100 text-green-700 dark:bg-green-900/30",
  beta: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  deprecated: "bg-red-100 text-red-700 dark:bg-red-900/30",
};

export function ApiVersionSelector({ versions, selected, onSelect }: ApiVersionSelectorProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">API Version</h3>
      <div className="space-y-2">
        {versions.map(v => (
          <button key={v.version} onClick={() => onSelect(v.version)}
            className={`flex w-full items-center justify-between rounded-lg border px-4 py-3 text-left transition ${selected === v.version ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "dark:border-gray-700"}`}>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold">{v.version}</span>
              <span className={`rounded px-1.5 py-0.5 text-xs ${statusBadge[v.status] ?? ""}`}>{v.status}</span>
            </div>
            <div className="text-xs text-gray-400">
              {v.sunsetDate ? `Sunset: ${v.sunsetDate}` : `Released: ${v.released}`}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
