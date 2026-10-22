"use client";

interface AppDetailTabsProps { activeTab: string; onTabChange: (tab: string) => void; hasWebhooks: boolean; hasSandbox: boolean; }

const TABS = [
  { key: "overview", label: "Overview", icon: "📋" },
  { key: "versions", label: "Versions", icon: "🏷️" },
  { key: "permissions", label: "Permissions", icon: "🔑" },
  { key: "reviews", label: "Reviews", icon: "⭐" },
];

export function AppDetailTabs({ activeTab, onTabChange, hasWebhooks, hasSandbox }: AppDetailTabsProps) {
  const tabs = [...TABS];
  if (hasWebhooks) tabs.push({ key: "webhooks", label: "Webhooks", icon: "🔔" });
  if (hasSandbox) tabs.push({ key: "sandbox", label: "Sandbox", icon: "📦" });
  return (
    <div className="flex gap-1 border-b border-gray-200 dark:border-gray-700">
      {tabs.map(t => (
        <button key={t.key} onClick={() => onTabChange(t.key)}
          className={`px-3 py-2 text-sm ${activeTab === t.key ? "border-b-2 border-blue-600 font-semibold text-blue-600" : "text-gray-500 hover:text-gray-700"}`}>
          {t.icon} {t.label}
        </button>
      ))}
    </div>
  );
}
