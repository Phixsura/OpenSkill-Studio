"use client";
export function FleetDspyPanel({ programs, deployed, modules, optimizations }: { programs: number; deployed: number; modules: number; optimizations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔬 DSPy</h3>
    <div className="text-sm">{deployed}/{programs} deployed · {modules} modules · {optimizations} opts</div>
  </div>);
}
