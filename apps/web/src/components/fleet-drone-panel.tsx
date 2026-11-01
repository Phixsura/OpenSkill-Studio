"use client";
export function FleetDronePanel({ total, success, failure, avgSteps, successRate }: { total: number; success: number; failure: number; avgSteps: number; successRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐝 Drone CI</h3>
    <div className="text-sm">{successRate}% success · {avgSteps} avg steps · {total} builds</div>
  </div>);
}
