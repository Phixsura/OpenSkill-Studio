"use client";
export function FleetApiCorsPolicyV9Panel({ policies, strict }: { policies: number; strict: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 CORS Policy v9</h3>
    <div className="text-sm">{policies} policies · {strict} strict</div>
  </div>);
}
