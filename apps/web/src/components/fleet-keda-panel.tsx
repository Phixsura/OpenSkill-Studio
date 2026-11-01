"use client";
export function FleetKedaPanel({ total, active, triggered, idle }: { total: number; active: number; triggered: number; idle: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 KEDA</h3>
    <div className="text-sm">{active}/{total} active · {triggered} triggered · {idle} idle</div>
  </div>);
}
