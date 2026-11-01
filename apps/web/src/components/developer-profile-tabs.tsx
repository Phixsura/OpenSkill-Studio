"use client";

interface DeveloperProfileTabsProps { activeTab: string; onTabChange: (tab: string) => void; appCount: number; }

export function DeveloperProfileTabs({ activeTab, onTabChange, appCount }: DeveloperProfileTabsProps) {
  const tabs = [
    { key: "apps", label: `Apps (${appCount})`, icon: "📦" },
    { key: "changelog", label: "Changelog", icon: "📋" },
    { key: "about", label: "About", icon: "ℹ️" },
  ];
  return (
    <div className="flex gap-1 border-b border-gray-200 dark:border-gray-700">
      {tabs.map(t => (
        <button key={t.key} onClick={() => onTabChange(t.key)}
          className={`px-4 py-2 text-sm ${activeTab === t.key ? "border-b-2 border-blue-600 font-semibold text-blue-600" : "text-gray-500"}`}>
          {t.icon} {t.label}
        </button>
      ))}
    </div>
  );
}
