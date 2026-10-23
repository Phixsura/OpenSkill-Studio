"use client";

interface InstalledApp { id: string; name: string; icon: string; version: string;
  installedAt: string; apiCalls30d: number; status: string;
  hasUpdate: boolean; updateVersion: string | null; }
interface InstalledAppsPageProps { apps: InstalledApp[]; totalApiCalls: number;
  updatesAvailable: number; onUninstall: (id: string) => void;
  onUpdate: (id: string) => void; onOpen: (id: string) => void; }

export function InstalledAppsPage({ apps, totalApiCalls, updatesAvailable,
  onUninstall, onUpdate, onOpen }: InstalledAppsPageProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📦 My Apps</h2>
        <div className="flex items-center gap-3 text-xs text-gray-400">
          <span>{apps.length} installed</span>
          <span>{totalApiCalls.toLocaleString()} API calls/30d</span>
          {updatesAvailable > 0 && <span className="text-blue-600">{updatesAvailable} updates</span>}
        </div>
      </div>
      <div className="space-y-2">
        {apps.map(a => (
          <div key={a.id} className="flex items-center justify-between rounded-xl border px-4 py-3 dark:border-gray-700">
            <div className="flex items-center gap-3 cursor-pointer" onClick={() => onOpen(a.id)}>
              <span className="text-2xl">{a.icon}</span>
              <div>
                <div className="flex items-center gap-2">
                  <p className="text-sm font-semibold">{a.name}</p>
                  <span className="text-xs text-gray-400">v{a.version}</span>
                  {a.hasUpdate && <span className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30">Update: v{a.updateVersion}</span>}
                </div>
                <p className="text-xs text-gray-400">{a.apiCalls30d.toLocaleString()} API calls</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {a.hasUpdate && <button onClick={() => onUpdate(a.id)} className="rounded bg-blue-600 px-2 py-1 text-xs text-white">Update</button>}
              <button onClick={() => onUninstall(a.id)} className="text-xs text-red-600 hover:underline">Uninstall</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
