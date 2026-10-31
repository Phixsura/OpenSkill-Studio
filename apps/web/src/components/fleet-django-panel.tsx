"use client";
export function FleetDjangoPanel({ apps, running, views, pendingMigrations }: { apps: number; running: number; views: number; pendingMigrations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐍 Django</h3>
    <div className="text-sm">{running}/{apps} running · {views} views</div>
    {pendingMigrations > 0 && <span className="text-xs text-yellow-600">⚠️ {pendingMigrations} pending migrations</span>}
  </div>);
}
