"use client";

interface TargetInfo {
  version: string;
  weight: number;
  request_count: number;
}

interface APITrafficSplitCardProps {
  targets: TargetInfo[];
  splitId: string;
  appName: string;
}

export default function APITrafficSplitCard({ targets, splitId, appName }: APITrafficSplitCardProps) {
  const totalReqs = targets.reduce((s, t) => s + t.request_count, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔀 Traffic Split</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {splitId}</p>
        </div>
        <span className="text-xs text-gray-400">{totalReqs.toLocaleString()} routed</span>
      </div>

      {targets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No traffic split</p>
      ) : (
        <div className="space-y-2">
          <div className="flex h-3 overflow-hidden rounded-full">
            {targets.map((t, i) => (
              <div key={t.version} className={`${i === 0 ? "bg-blue-500" : i === 1 ? "bg-green-500" : "bg-yellow-500"}`} style={{ width: `${t.weight}%` }} />
            ))}
          </div>
          <div className="space-y-1">
            {targets.map((t) => (
              <div key={t.version} className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{t.version}</span>
                <span className="text-gray-400">{t.weight}% · {t.request_count} reqs</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
