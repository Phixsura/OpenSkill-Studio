"use client";
export function FleetMixpanelPanel({ projects, active, events, users }: { projects: number; active: number; events: number; users: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Mixpanel</h3>
    <div className="text-sm">{active}/{projects} active · {events.toLocaleString()} events · {users.toLocaleString()} users</div>
  </div>);
}
