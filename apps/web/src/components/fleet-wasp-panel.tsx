"use client";
export function FleetWaspPanel({ apps, deployed, entities, operations }: { apps: number; deployed: number; entities: number; operations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐝 Wasp</h3>
    <div className="text-sm">{deployed}/{apps} deployed · {entities} entities · {operations} ops</div>
  </div>);
}
