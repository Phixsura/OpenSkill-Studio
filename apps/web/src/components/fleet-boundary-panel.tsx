"use client";
export function FleetBoundaryPanel({ targets, activeSessions, authorized }: { targets: number; activeSessions: number; authorized: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚪 Boundary</h3>
    <div className="text-sm">{targets} targets · {activeSessions} sessions · {authorized} authorized</div>
  </div>);
}
