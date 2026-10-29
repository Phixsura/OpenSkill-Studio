"use client";

interface MockInfo { mock_id: string; method: string; path: string; status_code: number; hit_count: number; }
interface Props { mocks: MockInfo[]; totalHits: number; appName: string; }

const methodColor: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600", PATCH: "text-purple-600" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiMockServerCard({ mocks, totalHits, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎭 Mock Server</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {mocks.length} mocks</p>
        </div>
        <span className="text-[10px] text-gray-400">{totalHits.toLocaleString()} hits</span>
      </div>
      {mocks.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No mocks defined</p>
      ) : (
        <div className="space-y-1">
          {mocks.map((m) => (
            <div key={m.mock_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`font-mono font-medium ${methodColor[m.method] ?? "text-gray-600"}`}>{m.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{m.path}</span>
              </div>
              <span className="text-gray-400">{m.status_code} · {m.hit_count}×</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
