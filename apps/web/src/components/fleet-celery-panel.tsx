"use client";
export function FleetCeleryPanel({ workers, online, activeTasks, reserved }: { workers: number; online: number; activeTasks: number; reserved: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🥬 Celery</h3>
    <div className="text-sm">{online}/{workers} online · {activeTasks} active · {reserved} reserved</div>
  </div>);
}
