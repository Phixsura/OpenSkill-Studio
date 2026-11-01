"use client";
export function FleetChangeApprPanel({ total, approved, unapproved, emergency, compliant }: { total: number; approved: number; unapproved: number; emergency: number; compliant: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✅ Change Approval</h3>
    <div className="text-sm">{approved}/{total} approved · {emergency} emergency</div>
    {!compliant && <span className="text-xs text-yellow-600">⚠️ {unapproved} unapproved changes</span>}
  </div>);
}
