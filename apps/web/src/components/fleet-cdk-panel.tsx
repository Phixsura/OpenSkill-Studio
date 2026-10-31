"use client";
export function FleetCdkPanel({ total, deployed, failed, drifted }: { total: number; deployed: number; failed: number; drifted: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏗️ AWS CDK</h3>
    <div className="text-sm">{deployed}/{total} deployed · {drifted} drifted</div>
    {failed > 0 && <span className="text-xs text-red-500">❌ {failed} failed</span>}
  </div>);
}
