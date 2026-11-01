"use client";

interface MaintenanceWindow { window_id: string; title: string; start_time: string;
  end_time: string; duration_min: number; affected_components: string[]; status: string; }
interface MaintenanceWindowBannerProps { active: MaintenanceWindow[]; upcoming: MaintenanceWindow[];
  onDismiss?: () => void; }

export function MaintenanceWindowBanner({ active, upcoming, onDismiss }: MaintenanceWindowBannerProps) {
  if (active.length === 0 && upcoming.length === 0) return null;
  return (
    <div className="space-y-2">
      {active.map(w => (
        <div key={w.window_id} className="rounded-lg border border-orange-300 bg-orange-50 p-4 dark:border-orange-700 dark:bg-orange-900/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="animate-pulse text-lg">🔧</span>
              <span className="font-semibold text-orange-700 dark:text-orange-400">Maintenance in Progress</span>
            </div>
            {onDismiss && <button onClick={onDismiss} className="text-gray-400">✕</button>}
          </div>
          <p className="mt-1 text-sm">{w.title}</p>
          <p className="text-xs text-gray-500">Affected: {w.affected_components.join(", ")}</p>
          <p className="text-xs text-gray-400">Expected completion: {new Date(w.end_time).toLocaleTimeString()}</p>
        </div>
      ))}
      {active.length === 0 && upcoming.slice(0, 1).map(w => (
        <div key={w.window_id} className="rounded-lg border border-blue-200 bg-blue-50 p-3 dark:border-blue-700 dark:bg-blue-900/10">
          <div className="flex items-center gap-2">
            <span>📅</span>
            <span className="text-sm font-medium">Upcoming: {w.title}</span>
            <span className="text-xs text-gray-400">{new Date(w.start_time).toLocaleString()} · {w.duration_min}min</span>
          </div>
        </div>
      ))}
    </div>
  );
}
