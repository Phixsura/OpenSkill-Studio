"use client";
export function FleetSurrealdbPanel({ instances, running, namespaces, tables }: { instances: number; running: number; namespaces: number; tables: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔮 SurrealDB</h3>
    <div className="text-sm">{running}/{instances} running · {namespaces} NS · {tables} tables</div>
  </div>);
}
