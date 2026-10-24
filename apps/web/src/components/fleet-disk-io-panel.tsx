"use client";
export function FleetDiskIoPanel({ readMbps, writeMbps, totalIops, saturated }: { readMbps: number; writeMbps: number; totalIops: number; saturated: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💾 Fleet Disk I/O</h3>
    <div className="text-sm">R {readMbps} · W {writeMbps} · Total {totalIops} MB/s</div>
    {saturated && <span className="text-xs text-red-500">⚠️ Disk saturated</span>}
  </div>);
}
