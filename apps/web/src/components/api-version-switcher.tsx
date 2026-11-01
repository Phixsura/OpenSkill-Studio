"use client";

interface VersionInfo { version: string; status: string; sunsetDate?: string; endpointCount: number; }
interface ApiVersionSwitcherProps { versions: VersionInfo[]; current: string;
  onSwitch: (version: string) => void; }

const STATUS_BADGE: Record<string, string> = {
  stable: "bg-green-100 text-green-700", deprecated: "bg-red-100 text-red-700",
  beta: "bg-blue-100 text-blue-700", alpha: "bg-purple-100 text-purple-700",
};

export function ApiVersionSwitcher({ versions, current, onSwitch }: ApiVersionSwitcherProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🔀 API Versions</h3>
      <div className="space-y-2">
        {versions.map(v => (
          <button key={v.version} onClick={() => onSwitch(v.version)}
            className={`w-full flex items-center justify-between px-4 py-3 rounded-lg text-left transition ${
              v.version === current ? "ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20" : "bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700"
            }`}>
            <div>
              <span className="text-sm font-bold font-mono">{v.version}</span>
              <span className="text-xs text-gray-400 ml-2">{v.endpointCount} endpoints</span>
              {v.sunsetDate && <span className="text-xs text-red-500 ml-2">Sunset: {v.sunsetDate}</span>}
            </div>
            <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_BADGE[v.status] || ""}`}>{v.status}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
