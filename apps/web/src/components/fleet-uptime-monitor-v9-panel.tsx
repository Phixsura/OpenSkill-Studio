"use client";
export function FleetUptimeMonitorV9Panel({ monitors, uptime }: { monitors: number; uptime: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏱️ Uptime Monitor v9</h3>
    <div className="text-sm">{monitors} monitors · {uptime}% uptime</div>
  </div>);
}
