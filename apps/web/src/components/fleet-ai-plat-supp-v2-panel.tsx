"use client";
export function FleetAiPlatSuppV2Panel({ systems, active, tickets, resolution, csat, slaMet }: { systems: number; active: number; tickets: number; resolution: number; csat: number; slaMet: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎧 AI Support v2</h3>
    <div className="text-sm">{active}/{systems} active · {tickets} tickets · {resolution}m resolution · ⭐ {csat} · SLA {slaMet}%</div>
  </div>);
}
