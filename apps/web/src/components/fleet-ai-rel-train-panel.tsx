"use client";
export function FleetAiRelTrainPanel({ trains, active, services, releases, onTime }: { trains: number; active: number; services: number; releases: number; onTime: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚂 AI Release Train</h3>
    <div className="text-sm">{active}/{trains} active · {services} services · {releases} releases · {onTime}% on-time</div>
  </div>);
}
