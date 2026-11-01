"use client";

interface Variant { id: string; name: string; weightPct: number; version: string; requests: number; errors: number; avgMs: number; }
interface Props { testId: string; endpoint: string; status: string; variants: Variant[]; appName: string; }

export default function APIDeveloperPlatformSDKConsumerApiEndpointAbTestCard({ testId, endpoint, status, variants, appName }: Props) {
  const statusColors: Record<string, string> = { draft: "bg-gray-200 text-gray-600", running: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400", completed: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400" };
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🧪 A/B Test</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — <code>{endpoint}</code></p>
        </div>
        <span className={`rounded px-2 py-0.5 text-[10px] font-bold ${statusColors[status] ?? ""}`}>{status}</span>
      </div>
      {variants.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No variants</p>
      ) : (
        <div className="space-y-2">
          {variants.map((v) => (
            <div key={v.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{v.name} ({v.version})</span>
                <span className="text-blue-600 font-bold">{v.weightPct}%</span>
              </div>
              {v.requests > 0 && <div className="mt-0.5 text-[10px] text-gray-400">{v.requests} req · {v.errors} err · {v.avgMs}ms avg</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
