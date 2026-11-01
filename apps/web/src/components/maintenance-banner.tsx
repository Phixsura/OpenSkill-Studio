"use client";

interface MaintenanceWindow { id: string; title: string; start: string; end: string;
  affected: string[]; severity: string; status: string; }
interface MaintenanceBannerProps { windows: MaintenanceWindow[]; }

export function MaintenanceBanner({ windows }: MaintenanceBannerProps) {
  const active = windows.filter(w => w.status === "in_progress");
  const upcoming = windows.filter(w => w.status === "scheduled");
  if (!active.length && !upcoming.length) return null;
  return (
    <div className="space-y-2">
      {active.map(w => (
        <div key={w.id} className="rounded-lg p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm">🔧</span>
            <span className="text-sm font-semibold text-red-700 dark:text-red-400">Maintenance in Progress</span>
          </div>
          <p className="text-sm text-red-600 dark:text-red-300">{w.title}</p>
          <p className="text-xs text-red-400 mt-1">
            Affected: {w.affected.join(", ")} · {w.start} – {w.end}
          </p>
        </div>
      ))}
      {upcoming.map(w => (
        <div key={w.id} className="rounded-lg p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm">📅</span>
            <span className="text-sm font-semibold text-yellow-700 dark:text-yellow-400">Scheduled Maintenance</span>
          </div>
          <p className="text-sm text-yellow-600 dark:text-yellow-300">{w.title}</p>
          <p className="text-xs text-yellow-400 mt-1">{w.start} – {w.end}</p>
        </div>
      ))}
    </div>
  );
}
