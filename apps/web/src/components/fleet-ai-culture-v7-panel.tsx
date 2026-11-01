"use client";
export function FleetAiCultureV7Panel({ trackers, active, enps, dx, hackathons }: { trackers: number; active: number; enps: number; dx: number; hackathons: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 AI Culture v7</h3>
    <div className="text-sm">{active}/{trackers} active · eNPS {enps} · DX {dx} · {hackathons} hackathons</div>
  </div>);
}
