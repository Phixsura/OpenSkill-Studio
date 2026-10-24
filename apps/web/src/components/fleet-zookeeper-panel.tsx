"use client";
export function FleetZookeeperPanel({ nodes, leader, followers, avgLatency, quorum }: { nodes: number; leader: number; followers: number; avgLatency: number; quorum: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🦓 Zookeeper</h3>
    <div className="text-sm">{leader}L/{followers}F · {avgLatency}ms avg</div>
    {!quorum && <span className="text-xs text-red-500">🚨 No quorum!</span>}
  </div>);
}
