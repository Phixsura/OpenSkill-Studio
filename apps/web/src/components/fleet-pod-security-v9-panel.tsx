"use client";
export function FleetPodSecurityV9Panel({ namespaces, restricted }: { namespaces: number; restricted: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 Pod Security v9</h3>
    <div className="text-sm">{namespaces} namespaces · {restricted} restricted</div>
  </div>);
}
