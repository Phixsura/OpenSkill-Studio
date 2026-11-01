"use client";
export function FleetNovuPanel({ environments, active, notifications, channels }: { environments: number; active: number; notifications: number; channels: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔔 Novu</h3>
    <div className="text-sm">{active}/{environments} active · {notifications.toLocaleString()} notifs · {channels} channels</div>
  </div>);
}
