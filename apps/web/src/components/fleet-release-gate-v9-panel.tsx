"use client";
export function FleetReleaseGateV9Panel({ releases, blocked }: { releases: number; blocked: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚧 Release Gate v9</h3>
    <div className="text-sm">{releases} releases · {blocked} blocked</div>
  </div>);
}
