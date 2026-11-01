"use client";
export function FleetSyntheticMonitorV9Panel({ checks, passing }: { checks: number; passing: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 Synthetic Monitor v9</h3>
    <div className="text-sm">{checks} checks · {passing} passing</div>
  </div>);
}
