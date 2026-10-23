"use client";

interface MaintenanceWindow { title: string; start: string; end: string; status: string; services: string[]; }
interface MaintenanceBannerProps { windows: MaintenanceWindow[]; hasActive: boolean; }

export function MaintenanceBanner({ windows, hasActive }: MaintenanceBannerProps) {
  const active = windows.filter(w => w.status === "in_progress");
  const upcoming = windows.filter(w => w.status === "scheduled");

  if (!hasActive && upcoming.length === 0) return null;

  return (
    <div className="space-y-2">
      {active.map((w, i) => (
        <div key={i} className="rounded-lg border-l-4 border-yellow-500 bg-yellow-50 p-3 dark:bg-yellow-900/10">
          <div className="flex items-center gap-2">
            <span className="animate-pulse">🔧</span>
            <p className="text-sm font-medium text-yellow-800 dark:text-yellow-300">Maintenance in progress: {w.title}</p>
          </div>
          <p className="mt-1 text-xs text-yellow-600">Affected: {w.services.join(", ")} · Until {new Date(w.end).toLocaleTimeString()}</p>
        </div>
      ))}
      {upcoming.slice(0, 2).map((w, i) => (
        <div key={i} className="rounded-lg border bg-blue-50 p-3 dark:bg-blue-900/10 dark:border-blue-800">
          <p className="text-sm text-blue-700 dark:text-blue-300">📅 Upcoming: {w.title} — {new Date(w.start).toLocaleDateString()}</p>
        </div>
      ))}
    </div>
  );
}
