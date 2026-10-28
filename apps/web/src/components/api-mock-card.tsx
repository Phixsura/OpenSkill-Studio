"use client";

interface MockInfo {
  mock_id: string;
  method: string;
  path: string;
  status_code: number;
  hit_count: number;
  delay_ms: number;
}

interface APIMockCardProps {
  mocks: MockInfo[];
  appName: string;
}

const METHOD_COLORS: Record<string, string> = {
  GET: "text-green-700 bg-green-100 dark:text-green-400 dark:bg-green-900/30",
  POST: "text-blue-700 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/30",
  PUT: "text-yellow-700 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/30",
  DELETE: "text-red-700 bg-red-100 dark:text-red-400 dark:bg-red-900/30",
};

export default function APIMockCard({ mocks, appName }: APIMockCardProps) {
  const totalHits = mocks.reduce((s, m) => s + m.hit_count, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">API Mocks</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {mocks.length} mocks · {totalHits} hits
        </span>
      </div>

      {mocks.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No mocks defined</p>
      ) : (
        <div className="space-y-1">
          {mocks.map((m) => (
            <div
              key={m.mock_id}
              className="flex items-center justify-between rounded px-2 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <div className="flex items-center gap-2">
                <span
                  className={`rounded px-1 py-0.5 text-[9px] font-bold ${METHOD_COLORS[m.method] ?? "bg-gray-100 text-gray-600"}`}
                >
                  {m.method}
                </span>
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">{m.path}</span>
                <span className="text-[10px] text-gray-400">→ {m.status_code}</span>
              </div>
              <span className="text-[11px] text-gray-400">{m.hit_count} hits</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
