"use client";
export function FleetCspPanel({ total, withCsp, strict, coveragePct }: { total: number; withCsp: number; strict: number; coveragePct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ CSP Coverage</h3>
    <div className="text-sm">{coveragePct}% with CSP · {strict} strict</div>
  </div>);
}
