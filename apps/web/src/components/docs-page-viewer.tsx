"use client";

interface Param { name: string; type: string; required: boolean; description: string; }
interface DocsPageViewerProps { method: string; path: string; description: string;
  parameters: Param[]; responses: Record<string, string>; }

const METHOD_COLORS: Record<string, string> = {
  GET: "bg-green-500", POST: "bg-blue-500", PUT: "bg-yellow-500",
  PATCH: "bg-orange-500", DELETE: "bg-red-500",
};

export function DocsPageViewer({ method, path, description, parameters, responses }: DocsPageViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <div className="flex items-center gap-2">
          <span className={`px-2 py-0.5 text-xs text-white rounded font-mono ${METHOD_COLORS[method] ?? "bg-gray-500"}`}>{method}</span>
          <span className="text-sm font-mono">{path}</span>
        </div>
        <div className="text-xs text-gray-400 mt-1">{description}</div>
      </div>
      {parameters.length > 0 && (
        <div className="border-b dark:border-gray-700 p-3">
          <div className="text-xs text-gray-400 mb-1">Parameters</div>
          {parameters.map(p => (
            <div key={p.name} className="flex items-center gap-2 text-xs py-0.5">
              <span className="font-mono font-medium">{p.name}</span>
              <span className="text-gray-400">{p.type}</span>
              {p.required && <span className="text-red-500 text-[10px]">required</span>}
              <span className="text-gray-400 ml-auto">{p.description}</span>
            </div>
          ))}
        </div>
      )}
      <div className="p-3">
        <div className="text-xs text-gray-400 mb-1">Responses</div>
        {Object.entries(responses).map(([code, desc]) => (
          <div key={code} className="flex gap-2 text-xs py-0.5">
            <span className={`font-mono font-bold ${code.startsWith("2") ? "text-green-600" : "text-red-500"}`}>{code}</span>
            <span className="text-gray-400">{desc}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
