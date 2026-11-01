"use client";

import { useState } from "react";

interface ClientMethod {
  name: string;
  method: string;
  path: string;
  hasBody: boolean;
  description: string;
}

interface GeneratedClient {
  className: string;
  baseUrl: string;
  authType: string;
  methods: ClientMethod[];
}

const methodColors: Record<string, string> = {
  GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600",
  DELETE: "text-red-600", PATCH: "text-purple-600",
};

export function ClientGeneratorPanel({
  client,
  generatedCode,
  onGenerate,
  onCopyCode,
}: {
  client: GeneratedClient | null;
  generatedCode: string;
  onGenerate?: (language: string) => void;
  onCopyCode?: () => void;
}) {
  const [lang, setLang] = useState<"typescript" | "python">("typescript");

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🔌 API Client Generator</h2>

      <div className="flex gap-2">
        {(["typescript", "python"] as const).map((l) => (
          <button key={l} onClick={() => setLang(l)}
            className={`text-sm px-3 py-1.5 rounded-lg ${lang === l ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {l === "typescript" ? "TypeScript" : "Python"}
          </button>
        ))}
        <button onClick={() => onGenerate?.(lang)}
          className="text-sm bg-green-600 text-white px-4 py-1.5 rounded-lg ml-auto">Generate</button>
      </div>

      {client && (
        <div className="rounded-lg border dark:border-gray-700 p-3 space-y-2">
          <div className="flex items-center gap-2">
            <code className="font-bold text-sm">{client.className}</code>
            <span className="text-xs text-gray-400">{client.baseUrl}</span>
            {client.authType && (
              <span className="text-xs bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 px-1.5 py-0.5 rounded">
                🔒 {client.authType}
              </span>
            )}
          </div>
          <div className="space-y-0.5">
            {client.methods.map((m) => (
              <div key={`${m.method}-${m.path}`} className="text-xs flex gap-2">
                <span className={`font-bold w-14 ${methodColors[m.method] || ""}`}>{m.method}</span>
                <code className="text-gray-500">{m.path}</code>
                <span className="text-gray-400">→ {m.name}()</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {generatedCode && (
        <div className="relative">
          <button onClick={onCopyCode}
            className="absolute top-2 right-2 text-xs bg-gray-700 text-white px-2 py-1 rounded">Copy</button>
          <pre className="rounded-lg border dark:border-gray-700 bg-gray-950 dark:bg-black p-3 text-xs text-green-400 font-mono overflow-x-auto max-h-64">
            {generatedCode}
          </pre>
        </div>
      )}
    </div>
  );
}
