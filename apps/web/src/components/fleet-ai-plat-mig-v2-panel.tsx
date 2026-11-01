"use client";
export function FleetAiPlatMigV2Panel({ migrations, running, completed, dataTb, zeroDowntime }: { migrations: number; running: number; completed: number; dataTb: number; zeroDowntime: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚚 AI Migration v2</h3>
    <div className="text-sm">{running} running · {completed} done · {dataTb}TB · {zeroDowntime ? "✅ zero-DT" : "⚠️"}</div>
  </div>);
}
