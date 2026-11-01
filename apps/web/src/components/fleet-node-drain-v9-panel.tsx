"use client";
export function FleetNodeDrainV9Panel({ nodes, draining }: { nodes: number; draining: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Node Drain v9</h3>
    <div className="text-sm">{nodes} nodes · {draining} draining</div>
  </div>);
}
