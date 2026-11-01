"use client";
export function FleetAiStatusV9Panel({ total, operational, uptime, status }: { total: number; operational: number; uptime: number; status: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🟢 AI Status v9</h3>
    <div className="text-sm">{operational}/{total} operational · {uptime}% uptime</div>
    <div className="text-xs mt-1 font-bold">{status}</div>
  </div>);
}
