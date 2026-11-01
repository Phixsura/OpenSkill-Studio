"use client";
export function FleetAiCompScanPanel({ scanners, active, scans, violations, autoFixed }: { scanners: number; active: number; scans: number; violations: number; autoFixed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 AI Compliance Scanner</h3>
    <div className="text-sm">{active}/{scanners} active · {scans.toLocaleString()} scans · {violations} violations · {autoFixed} auto-fixed</div>
  </div>);
}
