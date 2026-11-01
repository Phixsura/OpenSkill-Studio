"use client";
export function FleetAiPlatStorageV4Panel({ systems, active, total, used, iops }: { systems: number; active: number; total: number; used: number; iops: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💾 AI Storage v4</h3>
    <div className="text-sm">{active}/{systems} active · {used}/{total}PB · {iops.toLocaleString()} IOPS</div>
  </div>);
}
