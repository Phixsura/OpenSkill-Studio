"use client";

import { useState } from "react";

interface HealthBadgeEmbedProps { badgeUrl: string; markdown: string; htmlCode: string;
  status: string; uptimePct: number; onCopy: (text: string) => void; }

export function HealthBadgeEmbed({ badgeUrl, markdown, htmlCode, status, uptimePct, onCopy }: HealthBadgeEmbedProps) {
  const [tab, setTab] = useState<"markdown" | "html">("markdown");
  return (
    <div className="space-y-3 rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Health Badge</h3>
        <span className="text-xs text-gray-400">{uptimePct}% uptime</span>
      </div>
      <div className="flex justify-center rounded bg-gray-50 p-4 dark:bg-gray-800">
        <div className={`rounded-full px-3 py-1 text-xs font-bold text-white ${status === "healthy" ? "bg-green-500" : status === "degraded" ? "bg-yellow-500" : "bg-red-500"}`}>
          {status}
        </div>
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
        <span className="flex-1 truncate">{tab === "markdown" ? markdown : htmlCode}</span>
        <button onClick={() => onCopy(tab === "markdown" ? markdown : htmlCode)} className="text-blue-400">Copy</button>
      </div>
    </div>
  );
}
