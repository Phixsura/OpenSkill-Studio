"use client";
export function FleetJenkinsPanel({ controllers, online, agents, queueSize }: { controllers: number; online: number; agents: number; queueSize: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔨 Jenkins</h3>
    <div className="text-sm">{online}/{controllers} online · {agents} agents · queue {queueSize}</div>
  </div>);
}
