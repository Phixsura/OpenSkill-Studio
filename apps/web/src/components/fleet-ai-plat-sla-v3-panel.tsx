"use client";
export function FleetAiPlatSlaV3Panel({ managers, active, slas, met, breached, credits }: { managers: number; active: number; slas: number; met: number; breached: number; credits: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI SLA v3</h3>
    <div className="text-sm">{active}/{managers} active · {met}/{slas} met · {breached} breached · ${credits} credits</div>
  </div>);
}
