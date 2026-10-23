"use client";

interface AppItem { id: string; name: string; icon: string; status: string; installs: number; current: boolean; }
interface AppSwitcherDropdownProps { apps: AppItem[]; currentApp: AppItem | null;
  onSwitch: (id: string) => void; onCreateNew: () => void; }

const statusDot: Record<string, string> = { active: "bg-green-500", paused: "bg-yellow-500", inactive: "bg-gray-400" };

export function AppSwitcherDropdown({ apps, currentApp, onSwitch, onCreateNew }: AppSwitcherDropdownProps) {
  return (
    <div className="w-64 rounded-lg border bg-white shadow-lg dark:border-gray-700 dark:bg-gray-900">
      {currentApp && (
        <div className="border-b px-4 py-3 dark:border-gray-700">
          <p className="text-xs text-gray-400">Current App</p>
          <p className="font-bold">{currentApp.name}</p>
        </div>
      )}
      <div className="max-h-48 overflow-y-auto p-1">
        {apps.filter(a => !a.current).map(a => (
          <button key={a.id} onClick={() => onSwitch(a.id)}
            className="flex w-full items-center gap-2 rounded px-3 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-800">
            <div className="flex h-7 w-7 items-center justify-center rounded bg-gray-100 text-xs font-bold dark:bg-gray-800">
              {a.icon}
            </div>
            <div className="flex-1">
              <p className="font-medium">{a.name}</p>
              <p className="text-xs text-gray-400">{a.installs.toLocaleString()} installs</p>
            </div>
            <span className={`h-2 w-2 rounded-full ${statusDot[a.status] ?? statusDot.active}`} />
          </button>
        ))}
      </div>
      <div className="border-t p-1 dark:border-gray-700">
        <button onClick={onCreateNew}
          className="flex w-full items-center gap-2 rounded px-3 py-2 text-left text-sm text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/10">
          <span>➕</span> Create New App
        </button>
      </div>
    </div>
  );
}
