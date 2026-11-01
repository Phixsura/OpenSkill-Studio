"use client";
export function FleetDastScannerV9Panel({ scans, vulns }: { scans: number; vulns: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 DAST Scanner v9</h3>
    <div className="text-sm">{scans} scans · {vulns} vulnerabilities</div>
  </div>);
}
