"use client";

import { useState } from "react";

interface Tab { key: string; title: string; default?: boolean; }
interface AppDetailPageShellProps { appName: string; developerName: string; verified: boolean;
  tabs: Tab[]; installed: boolean; wishlisted: boolean;
  onInstall: () => void; onWishlist: () => void; children: React.ReactNode; }

export function AppDetailPageShell({ appName, developerName, verified, tabs, installed, wishlisted, onInstall, onWishlist, children }: AppDetailPageShellProps) {
  const [activeTab, setActiveTab] = useState(tabs.find(t => t.default)?.key || tabs[0]?.key || "");

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{appName}</h1>
          <p className="text-sm text-gray-500">{developerName} {verified && "✅"}</p>
        </div>
        <div className="flex gap-2">
          <button onClick={onWishlist} className={`rounded border px-3 py-2 text-sm ${wishlisted ? "border-red-300 text-red-600" : ""}`}>
            {wishlisted ? "❤️" : "🤍"}
          </button>
          <button onClick={onInstall} disabled={installed}
            className="rounded bg-blue-600 px-6 py-2 text-sm text-white disabled:opacity-50">
            {installed ? "Installed ✓" : "Install"}
          </button>
        </div>
      </div>
      <div className="flex border-b border-gray-200 dark:border-gray-700">
        {tabs.map(t => (
          <button key={t.key} onClick={() => setActiveTab(t.key)}
            className={`px-4 py-2.5 text-sm ${activeTab === t.key ? "border-b-2 border-blue-600 font-semibold text-blue-600" : "text-gray-500"}`}>
            {t.title}
          </button>
        ))}
      </div>
      <div>{children}</div>
    </div>
  );
}
