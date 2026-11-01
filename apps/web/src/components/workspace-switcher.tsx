"use client";

interface Workspace { name: string; app_count: number; }
interface WorkspaceSwitcherProps { workspaces: Workspace[]; active: string; onSwitch: (name: string) => void; onCreate: () => void; }

export function WorkspaceSwitcher({ workspaces, active, onSwitch, onCreate }: WorkspaceSwitcherProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-3 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Workspaces</h3>
        <button onClick={onCreate} className="text-xs text-blue-600">+ New</button>
      </div>
      <ul className="mt-2 space-y-1">
        {workspaces.map(w => (
          <li key={w.name}>
            <button onClick={() => onSwitch(w.name)}
              className={`flex w-full items-center justify-between rounded px-2 py-1.5 text-sm ${active === w.name ? "bg-blue-50 font-semibold text-blue-700 dark:bg-blue-900/20" : "text-gray-600 hover:bg-gray-50 dark:text-gray-400"}`}>
              <span>{w.name}</span>
              <span className="text-xs text-gray-400">{w.app_count} apps</span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
