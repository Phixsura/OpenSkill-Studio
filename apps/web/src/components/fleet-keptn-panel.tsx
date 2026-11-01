"use client";
export function FleetKeptnPanel({ total, deployed, evaluating, failed }: { total: number; deployed: number; evaluating: number; failed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 Keptn</h3>
    <div className="text-sm">{deployed} deployed · {evaluating} evaluating · {failed} failed</div>
  </div>);
}
