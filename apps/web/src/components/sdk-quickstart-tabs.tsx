"use client";
import { useState } from "react";

interface QuickstartTab { language: string; install: string; code: string; hasInstall: boolean; }
interface SdkQuickstartTabsProps { tabs: QuickstartTab[]; }

const LANG_ICON: Record<string, string> = {
  typescript: "🟦", python: "🐍", go: "🔵", curl: "💻",
};

export function SdkQuickstartTabs({ tabs }: SdkQuickstartTabsProps) {
  const [active, setActive] = useState(tabs[0]?.language || "");
  const current = tabs.find(t => t.language === active);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex border-b dark:border-gray-700">
        {tabs.map(t => (
          <button key={t.language} onClick={() => setActive(t.language)}
            className={`px-4 py-2 text-sm font-medium capitalize ${
              t.language === active ? "bg-white dark:bg-gray-900 border-b-2 border-blue-500" : "text-gray-500 hover:text-gray-700"
            }`}>{LANG_ICON[t.language] || ""} {t.language}</button>
        ))}
      </div>
      {current && (
        <div className="p-4 bg-gray-900 text-sm">
          {current.hasInstall && (
            <div className="mb-3">
              <p className="text-xs text-gray-400 mb-1">Install</p>
              <code className="text-green-400 text-xs">{current.install}</code>
            </div>
          )}
          <pre className="text-gray-300 text-xs whitespace-pre-wrap">{current.code}</pre>
        </div>
      )}
    </div>
  );
}
