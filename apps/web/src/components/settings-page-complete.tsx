"use client";

interface Tab { id: string; label: string; icon: string; active: boolean; }
interface SettingsPageCompleteProps { appName: string; version: string; tabs: Tab[];
  activeTab: string; children: React.ReactNode; onTabChange: (tab: string) => void; }

export function SettingsPageComplete({ appName, version, tabs, activeTab, children, onTabChange }: SettingsPageCompleteProps) {
  return (
    <div className="flex gap-6">
      <nav className="w-48 shrink-0 space-y-1">
        <div className="mb-4">
          <h2 className="text-sm font-bold">{appName}</h2>
          <p className="text-xs text-gray-400">v{version} · Settings</p>
        </div>
        {tabs.map(t => (
          <button key={t.id} onClick={() => onTabChange(t.id)}
            className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm ${t.active ? "bg-blue-50 text-blue-700 font-medium dark:bg-blue-900/20 dark:text-blue-300" : "text-gray-500 hover:bg-gray-50 dark:hover:bg-gray-800"}`}>
            <span>{t.icon}</span>{t.label}
          </button>
        ))}
      </nav>
      <div className="flex-1">{children}</div>
    </div>
  );
}
