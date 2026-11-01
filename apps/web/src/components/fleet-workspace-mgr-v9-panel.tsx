"use client";
export function FleetWorkspaceMgrV9Panel({ total, running }: { total: number; running: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🖥️ Workspace Manager v9</h3>
    <div className="text-sm">{total} workspaces · {running} running</div>
  </div>);
}
