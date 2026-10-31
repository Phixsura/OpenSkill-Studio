"use client";

import { useState } from "react";

interface EmbedWidgetConfiguratorProps { appName: string; iframeCode: string;
  scriptCode: string; previewUrl: string; onCopy: (code: string) => void; }

export function EmbedWidgetConfigurator({ appName, iframeCode, scriptCode, previewUrl, onCopy }: EmbedWidgetConfiguratorProps) {
  const [tab, setTab] = useState<"iframe" | "script">("iframe");
  const code = tab === "iframe" ? iframeCode : scriptCode;

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Embed {appName}</h2>
      <div className="rounded-lg border bg-gray-50 p-4 text-center dark:border-gray-700 dark:bg-gray-800">
        <p className="text-xs text-gray-400">Preview</p>
        <div className="mt-2 inline-block rounded border bg-white p-2 dark:bg-gray-900">
          <p className="text-sm">{appName} Widget</p>
        </div>
      </div>
      <div className="flex gap-1">
        {(["iframe", "script"] as const).map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`rounded px-3 py-1 text-xs ${tab === t ? "bg-blue-600 text-white" : "border dark:border-gray-600"}`}>
            {t === "iframe" ? "iFrame" : "Script Tag"}
          </button>
        ))}
      </div>
      <div className="flex items-center gap-2 rounded bg-gray-900 px-3 py-2 font-mono text-xs text-green-400">
        <span className="flex-1 truncate">{code}</span>
        <button onClick={() => onCopy(code)} className="flex-shrink-0 text-blue-400">Copy</button>
      </div>
    </div>
  );
}
