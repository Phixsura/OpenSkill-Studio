"use client";
export function FleetOpsgeniePanel({ teams, openAlerts, avgClose, withOnCall }: { teams: number; openAlerts: number; avgClose: number; withOnCall: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔔 OpsGenie</h3>
    <div className="text-sm">{teams} teams · {openAlerts} open · avg {avgClose}min close</div>
  </div>);
}
