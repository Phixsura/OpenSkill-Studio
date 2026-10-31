"use client";
export function FleetK9sPanel({ totalUsers, active, commands }: { totalUsers: number; active: number; commands: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐕 K9s</h3>
    <div className="text-sm">{active}/{totalUsers} active · {commands.toLocaleString()} commands/24h</div>
  </div>);
}
