"use client";
export function FleetIncidentResponseV9Panel({ teams, onCall }: { teams: number; onCall: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚨 Incident Response v9</h3>
    <div className="text-sm">{teams} teams · {onCall} on-call</div>
  </div>);
}
