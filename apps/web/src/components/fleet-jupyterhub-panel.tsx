"use client";
export function FleetJupyterhubPanel({ hubs, running, activeUsers, servers }: { hubs: number; running: number; activeUsers: number; servers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📓 JupyterHub</h3>
    <div className="text-sm">{running}/{hubs} running · {activeUsers} users · {servers} servers</div>
  </div>);
}
