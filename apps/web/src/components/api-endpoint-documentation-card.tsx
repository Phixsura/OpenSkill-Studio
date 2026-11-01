"use client";

interface DocInfo { method: string; path: string; summary: string; param_count: number; }
interface Props { docs: DocInfo[]; undocumentedCount: number; appName: string; }

export default function APIEndpointDocumentationCard({ docs, undocumentedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📖 Endpoint Docs</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{docs.length} documented</span>
          {undocumentedCount > 0 && <p className="text-[10px] text-yellow-600">{undocumentedCount} missing</p>}
        </div>
      </div>
      {docs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoint documentation</p>
      ) : (
        <div className="space-y-1">
          {docs.map((d) => (
            <div key={`${d.method}-${d.path}`} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-600 dark:bg-gray-800">{d.method}</span>
                <span className="font-mono text-gray-700 dark:text-gray-300">{d.path}</span>
              </div>
              <span className="text-gray-400">{d.param_count} params</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
