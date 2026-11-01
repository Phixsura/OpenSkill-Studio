"use client";
export function FleetAiSessionMgrPanel({ managers, active, sessions, duration, persistence }: { managers: number; active: number; sessions: number; duration: number; persistence: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 AI Session Manager</h3>
    <div className="text-sm">{active}/{managers} active · {sessions.toLocaleString()} sessions · {duration}m avg · {persistence}% persist</div>
  </div>);
}
