"use client";
export function FleetDbConnectionMonitorV9Panel({ pools, utilization }: { pools: number; utilization: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗄️ DB Connection Monitor v9</h3>
    <div className="text-sm">{pools} pools · {utilization}% utilized</div>
  </div>);
}
