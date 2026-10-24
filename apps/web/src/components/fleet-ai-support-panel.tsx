"use client";
export function FleetAiSupportPanel({ systems, active, tickets, autoResolved, resolution, csat }: { systems: number; active: number; tickets: number; autoResolved: number; resolution: number; csat: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎧 AI Support</h3>
    <div className="text-sm">{active}/{systems} active · {tickets.toLocaleString()} tickets · {autoResolved.toLocaleString()} auto · {resolution}m · ⭐ {csat}</div>
  </div>);
}
