"use client";
export function FleetDeployWinPanel({ total, inWindow, outWindow, compliant }: { total: number; inWindow: number; outWindow: number; compliant: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🕐 Deploy Windows</h3>
    {compliant ? <span className="text-xs text-green-600">✅ All {total} in window</span>
     : <span className="text-xs text-yellow-600">⚠️ {outWindow} outside maintenance window</span>}
  </div>);
}
