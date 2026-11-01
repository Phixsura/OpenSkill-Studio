"use client";

interface MockInfo { endpoint_id: string; method: string; path: string; status_code: number; enabled: boolean; hit_count: number; delay_ms: number; }
interface Props { mocks: MockInfo[]; appName: string; }

const mColor: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600" };

export default function APIDeveloperAPIApiMockServerCard({ mocks, appName }: Props) {
  const activeCount = mocks.filter(m => m.enabled).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎭 Mock Server</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCount}/{mocks.length} active</p>
      </div>
      {mocks.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No mocks configured</p>
      ) : (
        <div className="space-y-1.5">
          {mocks.map((m) => (
            <div key={m.endpoint_id} className={`flex items-center justify-between text-[11px] ${m.enabled ? "" : "opacity-40"}`}>
              <div className="flex items-center gap-1.5">
                <span className={`font-mono font-bold ${mColor[m.method] ?? "text-gray-500"}`}>{m.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{m.path}</span>
              </div>
              <span className="text-gray-400">{m.status_code} · {m.hit_count} hits</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
