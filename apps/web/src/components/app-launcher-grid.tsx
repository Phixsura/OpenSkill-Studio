"use client";

interface LauncherApp { id: string; name: string; icon: string; url: string; pinned: boolean; }
interface AppLauncherGridProps { apps: LauncherApp[]; onLaunch: (id: string) => void; onPin: (id: string) => void; }

export function AppLauncherGrid({ apps, onLaunch, onPin }: AppLauncherGridProps) {
  const pinned = apps.filter(a => a.pinned);
  const recent = apps.filter(a => !a.pinned);

  return (
    <div className="space-y-4">
      {pinned.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-gray-400 mb-2">📌 Pinned</p>
          <div className="grid grid-cols-4 gap-2">
            {pinned.map(a => (
              <button key={a.id} onClick={() => onLaunch(a.id)}
                className="flex flex-col items-center gap-1 rounded-lg border p-3 hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
                <span className="text-2xl">{a.icon}</span>
                <span className="text-xs font-medium truncate w-full text-center">{a.name}</span>
              </button>
            ))}
          </div>
        </div>
      )}
      {recent.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-gray-400 mb-2">Recent</p>
          <div className="grid grid-cols-4 gap-2">
            {recent.map(a => (
              <button key={a.id} onClick={() => onLaunch(a.id)}
                className="flex flex-col items-center gap-1 rounded-lg border p-3 hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
                <span className="text-2xl">{a.icon}</span>
                <span className="text-xs font-medium truncate w-full text-center">{a.name}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
