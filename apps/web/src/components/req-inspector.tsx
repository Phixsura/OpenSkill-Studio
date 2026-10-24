"use client";

interface ReqInspectorProps { method: string; path: string; headerCount: number;
  contentType: string; authType: string; bodySize: number; paramCount: number; }

const METHOD_COLORS: Record<string, string> = {
  GET: "bg-green-500", POST: "bg-blue-500", PUT: "bg-yellow-500",
  DELETE: "bg-red-500", PATCH: "bg-orange-500",
};

export function ReqInspector({ method, path, headerCount, contentType, authType, bodySize, paramCount }: ReqInspectorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center gap-2 p-4 border-b dark:border-gray-700">
        <span className={`px-2 py-0.5 text-xs text-white rounded ${METHOD_COLORS[method] ?? "bg-gray-500"}`}>{method}</span>
        <span className="text-sm font-mono">{path}</span>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Headers", v: headerCount }, { l: "Auth", v: authType },
          { l: "Body", v: `${bodySize}B` }, { l: "Params", v: paramCount }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-sm font-bold">{s.v}</div>
            <div className="text-[9px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
