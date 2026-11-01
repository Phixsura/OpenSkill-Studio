"use client";
export function FleetCloudwatchPanel({ total, ok, alarm, insufficient }: { total: number; ok: number; alarm: number; insufficient: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👁️ CloudWatch</h3>
    <div className="text-sm">🟢 {ok} · 🔴 {alarm} · ⚪ {insufficient} of {total}</div>
  </div>);
}
