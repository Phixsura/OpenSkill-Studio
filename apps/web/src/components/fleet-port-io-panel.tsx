"use client";
export function FleetPortIoPanel({ blueprints, entities, actions }: { blueprints: number; entities: number; actions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚢 Port.io</h3>
    <div className="text-sm">{blueprints} blueprints · {entities.toLocaleString()} entities · {actions} actions</div>
  </div>);
}
