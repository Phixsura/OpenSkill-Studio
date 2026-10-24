"use client";

import { useState } from "react";

interface EmbedCodeGeneratorProps { iframe: string; script: string; widgetUrl: string; }

export function EmbedCodeGenerator({ iframe, script, widgetUrl }: EmbedCodeGeneratorProps) {
  const [tab, setTab] = useState<"iframe" | "script">("iframe");
  const [copied, setCopied] = useState(false);
  const code = tab === "iframe" ? iframe : script;

  const copy = () => { navigator.clipboard?.writeText(code); setCopied(true); setTimeout(() => setCopied(false), 2000); };

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">Embed Code</h3>
      <div className="flex gap-1">
        {(["iframe", "script"] as const).map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`rounded px-3 py-1 text-xs capitalize ${tab === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{t}</button>
        ))}
      </div>
      <pre className="rounded-lg bg-gray-950 p-3 text-xs font-mono text-green-400 overflow-x-auto">{code}</pre>
      <div className="flex items-center justify-between">
        <a href={widgetUrl} target="_blank" rel="noopener" className="text-xs text-blue-600 hover:underline">Preview →</a>
        <button onClick={copy} className="rounded bg-gray-200 px-3 py-1 text-xs dark:bg-gray-700">{copied ? "✓ Copied" : "Copy"}</button>
      </div>
    </div>
  );
}
