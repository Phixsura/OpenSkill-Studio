"use client";
export function FleetSemkernelPanel({ apps, active, plugins, invocations }: { apps: number; active: number; plugins: number; invocations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧠 Semantic Kernel</h3>
    <div className="text-sm">{active}/{apps} active · {plugins} plugins · {invocations.toLocaleString()} inv</div>
  </div>);
}
