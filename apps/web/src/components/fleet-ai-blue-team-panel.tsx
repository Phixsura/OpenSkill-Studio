"use client";
export function FleetAiBlueTeamPanel({ teams, active, incidents, detections, responseMin }: { teams: number; active: number; incidents: number; detections: number; responseMin: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔵 AI Blue Teaming</h3>
    <div className="text-sm">{active}/{teams} active · {incidents} incidents · {detections} detections · {responseMin}m response</div>
  </div>);
}
