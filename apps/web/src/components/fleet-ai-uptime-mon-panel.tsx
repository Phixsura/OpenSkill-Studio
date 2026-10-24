"use client";
export function FleetAiUptimeMonPanel({ monitors, active, endpoints, uptime, checks }: { monitors: number; active: number; endpoints: number; uptime: number; checks: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⬆️ AI Uptime Monitor</h3>
    <div className="text-sm">{active}/{monitors} active · {endpoints} endpoints · {uptime}% uptime · {checks.toLocaleString()} checks</div>
  </div>);
}
