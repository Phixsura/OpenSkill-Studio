"use client";
export function FleetAiSupportV7Panel({ systems, active, tickets, res, csat, auto }: { systems: number; active: number; tickets: number; res: number; csat: number; auto: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎧 AI Support v7</h3>
    <div className="text-sm">{active}/{systems} active · {tickets.toLocaleString()} tickets · {res}m res · ⭐{csat} · {auto.toLocaleString()} auto</div>
  </div>);
}
