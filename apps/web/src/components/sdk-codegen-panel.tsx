"use client";

import { useState } from "react";

interface SdkCodegenPanelProps { generatedCode: Record<string, string>; languages: string[]; }

export function SdkCodegenPanel({ generatedCode, languages }: SdkCodegenPanelProps) {
  const [lang, setLang] = useState(languages[0] || "typescript");

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-2 border-b p-3 dark:border-gray-700">
        <h3 className="text-sm font-semibold">SDK Code</h3>
        <div className="ml-auto flex gap-1">
          {languages.map(l => (
            <button key={l} onClick={() => setLang(l)}
              className={`rounded px-2 py-0.5 text-xs ${lang === l ? "bg-blue-100 font-semibold text-blue-700" : "text-gray-500"}`}>
              {l}
            </button>
          ))}
        </div>
      </div>
      <pre className="max-h-64 overflow-auto p-3 text-xs font-mono text-gray-700 dark:text-gray-300">
        {generatedCode[lang] || "// Select a language"}
      </pre>
      <div className="border-t p-2 dark:border-gray-700">
        <button onClick={() => navigator.clipboard?.writeText(generatedCode[lang] || "")}
          className="rounded bg-gray-200 px-3 py-1 text-xs dark:bg-gray-700">📋 Copy</button>
      </div>
    </div>
  );
}
