"use client";
export function FleetResourceTaggingV9Panel({ total, compliant }: { total: number; compliant: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏷️ Resource Tagging v9</h3>
    <div className="text-sm">{total} resources · {compliant} compliant</div>
  </div>);
}
