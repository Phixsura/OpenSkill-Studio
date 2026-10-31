"use client";
import { useState } from "react";

interface Endpoint { path: string; method: string; description: string; params: { name: string; type: string; required: boolean }[]; }
interface Snippet { language: string; code: string; }

const methodColors: Record<string, string> = { GET: "bg-green-500", POST: "bg-blue-500", PUT: "bg-yellow-500", DELETE: "bg-red-500", PATCH: "bg-purple-500" };
const languages = ["curl", "python", "javascript"];

export function ApiPlaygroundExplorer({ endpoints, onGenerateSnippet }: {
  endpoints: Endpoint[]; onGenerateSnippet?: (path: string, method: string, lang: string) => Snippet | null;
}) {
  const [selected, setSelected] = useState<number | null>(null);
  const [lang, setLang] = useState("curl");
  const [snippet, setSnippet] = useState<Snippet | null>(null);
  const ep = selected !== null ? endpoints[selected] : null;

  return (
    <div className="space-y-3">
      <h3 className="font-bold text-sm">API Playground</h3>
      <div className="space-y-1">
        {endpoints.map((e, i) => (
          <button key={i} onClick={() => { setSelected(i); setSnippet(null); }}
            className={`w-full text-left border rounded-lg p-2 flex items-center gap-2 text-sm ${selected === i ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "border-gray-200 dark:border-gray-700"}`}>
            <span className={`text-[10px] text-white px-1.5 py-0.5 rounded font-bold ${methodColors[e.method] || "bg-gray-500"}`}>{e.method}</span>
            <span className="font-mono text-xs">{e.path}</span>
            <span className="text-xs text-gray-500 ml-auto">{e.description}</span>
          </button>
        ))}
      </div>
      {ep && (
        <div className="border dark:border-gray-700 rounded-xl p-4 space-y-2">
          <div className="flex gap-1">
            {languages.map(l => (
              <button key={l} onClick={() => { setLang(l); const s = onGenerateSnippet?.(ep.path, ep.method, l); if (s) setSnippet(s); }}
                className={`text-xs px-2 py-1 rounded ${lang === l ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{l}</button>
            ))}
          </div>
          {snippet && <pre className="bg-gray-900 text-green-400 rounded-lg p-3 text-xs font-mono overflow-x-auto">{snippet.code}</pre>}
        </div>
      )}
    </div>
  );
}
