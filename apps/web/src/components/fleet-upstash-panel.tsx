"use client";
export function FleetUpstashPanel({ databases, active, commands, bandwidthGb }: { databases: number; active: number; commands: number; bandwidthGb: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Upstash</h3>
    <div className="text-sm">{active}/{databases} active · {commands.toLocaleString()} cmds/24h · {bandwidthGb}GB</div>
  </div>);
}
