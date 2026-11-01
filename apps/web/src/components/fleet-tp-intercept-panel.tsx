"use client";
export function FleetTpInterceptPanel({ total, active, personal, globalInt }: { total: number; active: number; personal: number; globalInt: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔌 Intercepts</h3>
    <div className="text-sm">{active}/{total} active · {personal} personal · {globalInt} global</div>
  </div>);
}
