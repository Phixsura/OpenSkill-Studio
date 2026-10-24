"use client";
export function FleetAiMigrationPanel({ migrations, running, completed, failed, dataGb }: { migrations: number; running: number; completed: number; failed: number; dataGb: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚚 AI Migration</h3>
    <div className="text-sm">{running} running · {completed} done · {failed} failed · {dataGb} GB moved</div>
  </div>);
}
