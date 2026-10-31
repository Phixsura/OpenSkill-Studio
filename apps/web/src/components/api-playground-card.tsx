"use client";

interface TemplateInfo {
  request_id: string;
  method: string;
  path: string;
  name: string;
}

interface ResultInfo {
  request_id: string;
  status_code: number;
  duration_ms: number;
}

interface APIPlaygroundCardProps {
  templates: TemplateInfo[];
  recentResults: ResultInfo[];
  appName: string;
}

const methodColor: Record<string, string> = {
  GET: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  POST: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  PUT: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
  PATCH: "bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300",
  DELETE: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function APIPlaygroundCard({
  templates,
  recentResults,
  appName,
}: APIPlaygroundCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🎮 API Playground
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{templates.length} templates</span>
      </div>

      {templates.length > 0 && (
        <div className="mb-3 space-y-1">
          {templates.map((t) => (
            <div key={t.request_id} className="flex items-center gap-2 text-[11px]">
              <span
                className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${methodColor[t.method] ?? "bg-gray-100 text-gray-600"}`}
              >
                {t.method}
              </span>
              <span className="font-mono text-gray-600 dark:text-gray-400">{t.path}</span>
              {t.name && <span className="text-gray-400">— {t.name}</span>}
            </div>
          ))}
        </div>
      )}

      {recentResults.length > 0 && (
        <>
          <p className="mb-1 text-[10px] text-gray-500">Recent results</p>
          <div className="space-y-0.5">
            {recentResults.slice(0, 5).map((r, i) => (
              <div key={i} className="flex items-center justify-between text-[11px]">
                <span className={r.status_code < 400 ? "text-green-600" : "text-red-500"}>
                  {r.status_code}
                </span>
                <span className="text-gray-400">{r.duration_ms}ms</span>
              </div>
            ))}
          </div>
        </>
      )}

      {templates.length === 0 && recentResults.length === 0 && (
        <p className="text-center text-sm text-gray-400">No playground activity</p>
      )}
    </div>
  );
}
