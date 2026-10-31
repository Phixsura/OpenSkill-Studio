"use client";

interface EndpointInfo { method: string; path: string; summary: string; tags: string[]; has_examples: boolean; }
interface Props { title: string; version: string; endpoints: EndpointInfo[]; documentedPct: number; appName: string; }

const mColor: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600", PATCH: "text-orange-600" };

export default function APIDeveloperAPIApiDeveloperApiApiApiDocumentationGeneratorCard({ title, version, endpoints, documentedPct, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📚 API Docs Generator</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{title} v{version}</p>
        </div>
        <span className="text-[10px] text-gray-400">{documentedPct}% with examples</span>
      </div>
      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoints documented</p>
      ) : (
        <div className="space-y-1">
          {endpoints.slice(0, 8).map((e, i) => (
            <div key={i} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`font-mono font-bold ${mColor[e.method] ?? "text-gray-500"}`}>{e.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{e.path}</span>
              </div>
              {e.has_examples && <span className="text-[9px] text-green-500">✓</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
