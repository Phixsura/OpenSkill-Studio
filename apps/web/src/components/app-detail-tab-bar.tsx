"use client";

interface Tab { key: string; title: string; }
interface AppDetailTabBarProps { tabs: Tab[]; activeTab: string; onTabChange: (key: string) => void; }

export function AppDetailTabBar({ tabs, activeTab, onTabChange }: AppDetailTabBarProps) {
  return (
    <div className="flex border-b border-gray-200 dark:border-gray-700">
      {tabs.map(tab => (
        <button key={tab.key} onClick={() => onTabChange(tab.key)}
          className={`px-4 py-2.5 text-sm transition ${activeTab === tab.key
            ? "border-b-2 border-blue-600 font-semibold text-blue-600"
            : "text-gray-500 hover:text-gray-700 dark:text-gray-400"}`}>
          {tab.title}
        </button>
      ))}
    </div>
  );
}
