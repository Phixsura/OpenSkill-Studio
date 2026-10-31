"use client";

interface ExecutionInfo { execution_id: string; method: string; path: string; status_code: number; duration_ms: number; }
interface Props { executions: ExecutionInfo[]; avgDuration: number; appName: string; }

const methodColor: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", PATCH: "text-orange-600", DELETE: "text-red-600" };

export default function APIDeveloperAPIApiPlaygroundRunnerCard({ executions, avgDuration, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">▶️ Playground Runner</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">avg: {avgDuration}ms</span>
      </div>
      {executions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No executions</p>
      ) : (
        <div className="space-y-1">
          {executions.map((e) => (
            <div key={e.execution_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`font-mono font-bold ${methodColor[e.method] ?? "text-gray-500"}`}>{e.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{e.path}</span>
              </div>
              <span className={`font-mono ${e.status_code >= 400 ? "text-red-500" : "text-green-600"}`}>{e.status_code} · {e.duration_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
