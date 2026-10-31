"use client";
export function FleetSidekiqPanel({ processes, busy, enqueued, dead }: { processes: number; busy: number; enqueued: number; dead: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💎 Sidekiq</h3>
    <div className="text-sm">{processes} processes · {busy} busy · {enqueued} enqueued</div>
    {dead > 0 && <span className="text-xs text-red-500">💀 {dead} dead jobs</span>}
  </div>);
}
