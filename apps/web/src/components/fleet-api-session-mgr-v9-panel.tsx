"use client";
export function FleetApiSessionMgrV9Panel({ sessions, active }: { sessions: number; active: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎫 API Session v9</h3>
    <div className="text-sm">{sessions} sessions · {active} active</div>
  </div>);
}
