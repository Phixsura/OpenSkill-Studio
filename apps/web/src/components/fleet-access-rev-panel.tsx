"use client";
export function FleetAccessRevPanel({ total, reviewed, pendingReview, excessPermissions, clean }: { total: number; reviewed: number; pendingReview: number; excessPermissions: number; clean: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👥 Access Review</h3>
    <div className="text-sm">{reviewed}/{total} reviewed</div>
    {!clean && <span className="text-xs text-yellow-600">⚠️ {excessPermissions} excess permissions</span>}
  </div>);
}
