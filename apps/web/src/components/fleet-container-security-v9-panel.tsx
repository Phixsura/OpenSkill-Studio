"use client";
export function FleetContainerSecurityV9Panel({ containers, nonRoot }: { containers: number; nonRoot: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐳 Container Security v9</h3>
    <div className="text-sm">{containers} containers · {nonRoot} non-root</div>
  </div>);
}
