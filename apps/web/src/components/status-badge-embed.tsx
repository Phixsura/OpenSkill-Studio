"use client";

import { useState } from "react";

interface StatusBadgeEmbedProps { badgeUrl: string; markdownSnippet: string;
  htmlSnippet: string; onCopy: (text: string) => void; }

export function StatusBadgeEmbed({ badgeUrl, markdownSnippet, htmlSnippet, onCopy }: StatusBadgeEmbedProps) {
  const [tab, setTab] = useState<"markdown" | "html">("markdown");
  const snippet = tab === "markdown" ? markdownSnippet : htmlSnippet;

  return (
    <div className="space-y-3 rounded-lg border p-4 dark:border-gray-700">
      <h3 className="text-sm font-semibold">Status Badge</h3>
      <div className="flex justify-center rounded bg-gray-50 p-4 dark:bg-gray-800">
        <img src={badgeUrl} alt="Status badge" className="h-5" />
      </div>
      <div className="flex gap-1">
        {(["markdown", "html"] as const).map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`rounded px-3 py-1 text-xs capitalize ${tab === t ? "bg-blue-600 text-white" : "border dark:border-gray-600"}`}>
            {t}
          </button>
        ))}
      </div>
      <div className="flex items-center gap-2 rounded bg-gray-900 px-3 py-2 font-mono text-xs text-green-400">
        <span className="flex-1 truncate">{snippet}</span>
        <button onClick={() => onCopy(snippet)} className="flex-shrink-0 text-blue-400">Copy</button>
      </div>
    </div>
  );
}
