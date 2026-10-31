"use client";
export function FleetMarimoPanel({ notebooks, running, cells, users }: { notebooks: number; running: number; cells: number; users: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📓 Marimo</h3>
    <div className="text-sm">{running}/{notebooks} running · {cells} cells · {users.toLocaleString()} users</div>
  </div>);
}
