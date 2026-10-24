"use client";

interface Tab { id: string; label: string; icon: string; }
interface TabNavigationProps { tabs: Tab[]; activeTab: string; onTabChange: (id: string) => void; }

export function TabNavigation({ tabs, activeTab, onTabChange }: TabNavigationProps) {
  return (
    <div className="border-b dark:border-gray-700">
      <div className="flex gap-1 overflow-x-auto">
        {tabs.map(tab => (
          <button key={tab.id} onClick={() => onTabChange(tab.id)}
            className={`flex items-center gap-1.5 whitespace-nowrap border-b-2 px-4 py-2.5 text-sm ${
              activeTab === tab.id
                ? "border-blue-600 font-semibold text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400"
            }`}>
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
