"use client";
export function FleetAiDevsecopsV8Panel({ systems, active, scans, vulns, fixed, sast }: { systems: number; active: number; scans: number; vulns: number; fixed: number; sast: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 AI DevSecOps v8</h3>
    <div className="text-sm">{active}/{systems} active · {scans.toLocaleString()} scans · {vulns} vulns · {fixed} fixed · SAST {sast}%</div>
  </div>);
}
