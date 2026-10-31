"use client";
export function FleetDependencyScannerV9Panel({ deps, vulnerable }: { deps: number; vulnerable: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔎 Dependency Scanner v9</h3>
    <div className="text-sm">{deps} deps · {vulnerable} vulnerable</div>
  </div>);
}
