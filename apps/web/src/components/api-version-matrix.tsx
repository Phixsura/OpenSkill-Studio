"use client";

interface ApiVersion { version: string; status: string; releaseDate: string; }
interface ApiVersionMatrixProps { versions: ApiVersion[]; latest: string | null;
  activeCount: number; deprecatedCount: number; }

const STATUS_STYLE: Record<string, { bg: string; icon: string }> = {
  active: { bg: "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400", icon: "🟢" },
  beta: { bg: "bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400", icon: "🔵" },
  deprecated: { bg: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400", icon: "🟡" },
  sunset: { bg: "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400", icon: "🔴" },
};

export function ApiVersionMatrix({ versions, latest, activeCount, deprecatedCount }: ApiVersionMatrixProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📦 API Versions</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{activeCount} active</span>
          {deprecatedCount > 0 && <span className="text-yellow-600">{deprecatedCount} deprecated</span>}
          {latest && <span className="text-gray-400">latest: {latest}</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {versions.map(v => {
          const s = STATUS_STYLE[v.status] ?? STATUS_STYLE.active;
          return (
            <div key={v.version} className="flex items-center justify-between px-4 py-2.5">
              <div className="flex items-center gap-2">
                <span>{s.icon}</span>
                <span className="text-sm font-mono font-medium">{v.version}</span>
                {v.version === latest && <span className="text-[10px] text-blue-500">★ latest</span>}
              </div>
              <div className="flex items-center gap-2">
                {v.releaseDate && <span className="text-xs text-gray-400">{v.releaseDate}</span>}
                <span className={`px-2 py-0.5 text-[10px] rounded-full ${s.bg}`}>{v.status}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
