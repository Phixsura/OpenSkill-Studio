"use client";
export function FleetClerkPanel({ apps, active, users, sessions }: { apps: number; active: number; users: number; sessions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔑 Clerk</h3>
    <div className="text-sm">{active}/{apps} active · {users.toLocaleString()} users · {sessions.toLocaleString()} sessions</div>
  </div>);
}
