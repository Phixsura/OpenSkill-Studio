"use client";
export function FleetDataRetentionV9Panel({ policies, compliant }: { policies: number; compliant: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📂 Data Retention v9</h3>
    <div className="text-sm">{policies} policies · {compliant} compliant</div>
  </div>);
}
