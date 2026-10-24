"use client";
export function FleetLeadTimePanel({ total, avgLeadTime, underHour, elite }: { total: number; avgLeadTime: number; underHour: number; elite: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏱️ Lead Time</h3>
    <div className="text-sm">avg {avgLeadTime}min · {underHour}/{total} under 1hr</div>
    {elite && <span className="text-xs text-green-600">🏆 Elite performance</span>}
  </div>);
}
