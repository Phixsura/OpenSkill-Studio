"use client";
export function FleetKpiDashPanel({ uptimePct, userGrowth, revenueGrowth, healthy }: { uptimePct: number; userGrowth: number; revenueGrowth: number; healthy: boolean; }) {
  return (<div className="rounded-2xl border-2 dark:border-gray-600 p-6">
    <h3 className="font-semibold mb-2 text-center">📊 Platform KPIs</h3>
    <div className="grid grid-cols-3 gap-3 text-center text-sm">
      <div><div className="font-bold">{uptimePct}%</div><div className="text-xs text-gray-400">Uptime</div></div>
      <div><div className="font-bold text-green-600">+{userGrowth}%</div><div className="text-xs text-gray-400">Users</div></div>
      <div><div className="font-bold text-green-600">+{revenueGrowth}%</div><div className="text-xs text-gray-400">Revenue</div></div>
    </div>
  </div>);
}
