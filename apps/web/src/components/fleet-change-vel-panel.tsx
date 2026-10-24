"use client";
export function FleetChangeVelPanel({ deploys, hours, ratePerHour, highVelocity }: { deploys: number; hours: number; ratePerHour: number; highVelocity: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 Change Velocity</h3>
    <div className="text-sm">{deploys} deploys / {hours}h = {ratePerHour}/hr</div>
    {highVelocity && <span className="text-xs text-blue-500">⚡ High velocity</span>}
  </div>);
}
