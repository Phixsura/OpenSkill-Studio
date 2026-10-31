"use client";

import { useState } from "react";

interface SharePageLayoutProps { appName: string; appUrl: string; twitterUrl: string; linkedinUrl: string;
  badgeCode: string; buttonCode: string; qrUrl: string; }

export function SharePageLayout({ appName, appUrl, twitterUrl, linkedinUrl, badgeCode, buttonCode, qrUrl }: SharePageLayoutProps) {
  const [tab, setTab] = useState<"link" | "badge" | "button">("link");
  const content = { link: appUrl, badge: badgeCode, button: buttonCode };

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h1 className="text-2xl font-bold">Share {appName}</h1>
      <div className="flex gap-3">
        <a href={twitterUrl} target="_blank" rel="noopener noreferrer"
          className="flex-1 rounded-lg border border-gray-200 py-3 text-center text-sm hover:bg-gray-50 dark:border-gray-700">
          🐦 Twitter
        </a>
        <a href={linkedinUrl} target="_blank" rel="noopener noreferrer"
          className="flex-1 rounded-lg border border-gray-200 py-3 text-center text-sm hover:bg-gray-50 dark:border-gray-700">
          💼 LinkedIn
        </a>
      </div>
      <div>
        <div className="flex gap-1">
          {(["link", "badge", "button"] as const).map(t => (
            <button key={t} onClick={() => setTab(t)}
              className={`rounded px-3 py-1 text-xs capitalize ${tab === t ? "bg-blue-100 font-semibold text-blue-700" : "text-gray-500"}`}>
              {t}
            </button>
          ))}
        </div>
        <pre className="mt-2 overflow-x-auto rounded bg-gray-50 p-3 text-xs dark:bg-gray-800">
          <code>{content[tab]}</code>
        </pre>
        <button onClick={() => navigator.clipboard?.writeText(content[tab])}
          className="mt-2 rounded bg-gray-200 px-3 py-1 text-xs dark:bg-gray-700">Copy</button>
      </div>
    </div>
  );
}
