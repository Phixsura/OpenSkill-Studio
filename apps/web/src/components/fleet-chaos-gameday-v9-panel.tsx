"use client";
export function FleetChaosGamedayV9Panel({ gamedays, findings }: { gamedays: number; findings: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎮 Chaos GameDay v9</h3>
    <div className="text-sm">{gamedays} gamedays · {findings} findings</div>
  </div>);
}
