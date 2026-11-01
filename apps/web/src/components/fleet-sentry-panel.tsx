"use client";
export function FleetSentryPanel({ projects, events, unresolved, crashFree }: { projects: number; events: number; unresolved: number; crashFree: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐛 Sentry</h3>
    <div className="text-sm">{projects} projects · {events.toLocaleString()} events · {crashFree}% crash-free</div>
    {unresolved > 0 && <span className="text-xs text-yellow-600">⚠️ {unresolved} unresolved</span>}
  </div>);
}
