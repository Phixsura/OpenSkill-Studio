"use client";

interface VersionInfo { version: string; status: string; sunsetDate: string; }
interface ApiVersionPanelProps { versions: VersionInfo[]; latest: string; total: number; }

const STATUS_STYLE: Record<string, string> = {
  active: "text-green-600", deprecated: "text-yellow-600", sunset: "text-red-500",
};

export function ApiVersionPanel({ versions, latest, total }: ApiVersionPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📌 API Versions</h3>
        <span className="text-xs text-gray-400">latest: {latest} · {total} versions</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {versions.map(v => (
          <div key={v.version} className="flex items-center justify-between px-4 py-2 text-xs">
            <span className="font-mono font-bold">{v.version}</span>
            <div className="flex items-center gap-2">
              {v.sunsetDate && <span className="text-gray-400">sunset: {v.sunsetDate}</span>}
              <span className={`font-bold ${STATUS_STYLE[v.status] ?? ""}`}>{v.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
