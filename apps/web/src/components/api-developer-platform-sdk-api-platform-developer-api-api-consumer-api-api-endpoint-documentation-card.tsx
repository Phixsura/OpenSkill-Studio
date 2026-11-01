"use client";

interface DocInfo { endpoint: string; method: string; summary: string; tags: string[]; has_examples: boolean; }
interface Props { docs: DocInfo[]; totalDocs: number; undocumentedCount: number; appName: string; }

const methodColor: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointDocumentationCard({ docs, totalDocs, undocumentedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📖 API Docs</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalDocs} documented</p>
        </div>
        {undocumentedCount > 0 && <span className="text-[10px] text-amber-600 dark:text-amber-400">⚠️ {undocumentedCount} missing</span>}
      </div>
      {docs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No documentation</p>
      ) : (
        <div className="space-y-1">
          {docs.map((d) => (
            <div key={`${d.method}-${d.endpoint}`} className="text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`font-mono font-medium ${methodColor[d.method] ?? "text-gray-600"}`}>{d.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{d.endpoint}</span>
              </div>
              <div className="text-[10px] text-gray-400">{d.summary}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
