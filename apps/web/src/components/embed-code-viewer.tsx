"use client";

import { useState } from "react";

interface EmbedCodeViewerProps { iframe: string; badge: string; directLink: string; }

export function EmbedCodeViewer({ iframe, badge, directLink }: EmbedCodeViewerProps) {
  const [tab, setTab] = useState<"iframe" | "badge" | "link">("iframe");
  const content = { iframe, badge, link: directLink };

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Embed Code</h3>
      <div className="mt-2 flex gap-2">
        {(["iframe", "badge", "link"] as const).map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`rounded px-3 py-1 text-xs ${tab === t ? "bg-blue-100 text-blue-700" : "text-gray-500"}`}>
            {t === "iframe" ? "Widget" : t === "badge" ? "Badge" : "Link"}
          </button>
        ))}
      </div>
      <pre className="mt-3 overflow-x-auto rounded bg-gray-50 p-3 text-xs dark:bg-gray-900">
        <code>{content[tab]}</code>
      </pre>
      <button onClick={() => navigator.clipboard?.writeText(content[tab])}
        className="mt-2 rounded bg-gray-200 px-3 py-1 text-xs hover:bg-gray-300 dark:bg-gray-700">
        📋 Copy
      </button>
    </div>
  );
}
