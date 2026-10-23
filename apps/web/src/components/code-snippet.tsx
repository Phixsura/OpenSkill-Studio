"use client";

import { useState } from "react";

interface CodeLine { number: number; content: string; }
interface CodeSnippetProps { language: string; icon: string; title: string | null;
  lines: CodeLine[]; showLineNumbers: boolean; }

export function CodeSnippet({ language, icon, title, lines, showLineNumbers }: CodeSnippetProps) {
  const [copied, setCopied] = useState(false);
  const raw = lines.map(l => l.content).join("\n");
  const copy = () => { navigator.clipboard?.writeText(raw); setCopied(true); setTimeout(() => setCopied(false), 2000); };

  return (
    <div className="rounded-lg border overflow-hidden dark:border-gray-700">
      <div className="flex items-center justify-between border-b bg-gray-50 px-4 py-2 dark:bg-gray-900 dark:border-gray-700">
        <div className="flex items-center gap-2 text-xs">
          <span>{icon}</span>
          {title && <span className="font-medium">{title}</span>}
          <span className="text-gray-400">{language}</span>
        </div>
        <button onClick={copy} className="text-xs text-gray-400 hover:text-gray-600">{copied ? "Copied!" : "Copy"}</button>
      </div>
      <pre className="overflow-x-auto p-4 text-sm bg-gray-950 text-gray-200">
        {lines.map(l => (
          <div key={l.number} className="flex">
            {showLineNumbers && <span className="mr-4 select-none text-right text-gray-600 w-8">{l.number}</span>}
            <code dangerouslySetInnerHTML={{ __html: l.content }} />
          </div>
        ))}
      </pre>
    </div>
  );
}
