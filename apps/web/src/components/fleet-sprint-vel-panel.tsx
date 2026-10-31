"use client";
export function FleetSprintVelPanel({ sprints, avgVelocity, latest, trend }: { sprints: number; avgVelocity: number; latest: number; trend: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏃 Sprint Velocity</h3>
    <div className="text-sm">avg {avgVelocity} pts · latest {latest} · {trend}</div>
  </div>);
}
