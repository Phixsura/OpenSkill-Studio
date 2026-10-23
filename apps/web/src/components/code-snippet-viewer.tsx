"use client";

import { useState } from "react";

interface CodeSnippetViewerProps { title: string; languages: { id: string; code: string }[];
  onCopy: (code: string) => void; }

export function CodeSnippetViewer({ title, languages, onCopy }: CodeSnippetViewerProps) {
  const [active, setActive] = useState(languages[0]?.id ?? "");
  const current = languages.find(l => l.id === active);

  return (
    <div className="rounded-lg border dark:border-gray-700">
      <div className="flex items-center justify-between border-b px-4 py-2 dark:border-gray-700">
        <h3 className="text-sm font-semibold">{title}</h3>
        <div className="flex gap-1">
          {languages.map(l => (
            <button key={l.id} onClick={() => setActive(l.id)}
              className={`rounded px-2 py-0.5 text-xs ${active === l.id ? "bg-blue-600 text-white" : "text-gray-400 hover:text-gray-600"}`}>
              {l.id}
            </button>
          ))}
        </div>
      </div>
      <div className="relative">
        <pre className="overflow-x-auto p-4 font-mono text-xs leading-relaxed text-gray-700 dark:text-gray-300">
          {current?.code ?? ""}
        </pre>
        <button onClick={() => current && onCopy(current.code)}
          className="absolute right-2 top-2 rounded border bg-white px-2 py-0.5 text-xs dark:border-gray-600 dark:bg-gray-800">
          Copy
        </button>
      </div>
    </div>
  );
}
