"use client";
export function FleetApiSecurityScanV9Panel({ scans, findings }: { scans: number; findings: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 API Security Scan v9</h3>
    <div className="text-sm">{scans} scans · {findings} OWASP findings</div>
  </div>);
}
