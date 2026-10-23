"use client";

import { useState } from "react";

interface Tab { key: string; title: string; icon: string; }
interface DeveloperSettingsLayoutProps { tabs: Tab[]; children: React.ReactNode; }

export function DeveloperSettingsLayout({ tabs, children }: DeveloperSettingsLayoutProps) {
  const [activeTab, setActiveTab] = useState(tabs[0]?.key || "");

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Settings</h1>
      <div className="flex gap-6">
        <nav className="w-52 space-y-0.5">
          {tabs.map(tab => (
            <button key={tab.key} onClick={() => setActiveTab(tab.key)}
              className={`flex w-full items-center gap-2 rounded px-3 py-2 text-left text-sm ${
                activeTab === tab.key ? "bg-blue-50 font-semibold text-blue-700 dark:bg-blue-900/20"
                : "text-gray-600 hover:bg-gray-50 dark:text-gray-400"}`}>
              <span>{tab.icon}</span>{tab.title}
            </button>
          ))}
        </nav>
        <div className="flex-1 rounded-lg border border-gray-200 p-6 dark:border-gray-700">
          {children}
        </div>
      </div>
    </div>
  );
}
