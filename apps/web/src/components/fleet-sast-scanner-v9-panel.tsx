"use client";
export function FleetSastScannerV9Panel({ scans, critical }: { scans: number; critical: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 SAST Scanner v9</h3>
    <div className="text-sm">{scans} scans · {critical} critical</div>
  </div>);
}
