"use client";
export function FleetContainerRuntimeV9Panel({ containers, running }: { containers: number; running: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐳 Container Runtime v9</h3>
    <div className="text-sm">{containers} containers · {running} running</div>
  </div>);
}
