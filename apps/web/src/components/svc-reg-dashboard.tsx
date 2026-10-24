"use client";

interface SvcRegDashboardProps { total: number; healthy: number; unhealthy: number;
  healthPct: number; byTeam: Record<string, number>; byType: Record<string, number>; }

export function SvcRegDashboard({ total, healthy, unhealthy, healthPct, byTeam, byType }: SvcRegDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Service Registry</h3>
        <span className="text-xs text-gray-400">{total} services · {healthPct}% healthy</span>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        <div className="bg-white dark:bg-gray-900 p-3 text-center"><div className="text-lg font-bold">{total}</div><div className="text-[10px] text-gray-400">Total</div></div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center"><div className="text-lg font-bold text-green-600">{healthy}</div><div className="text-[10px] text-gray-400">Healthy</div></div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center"><div className="text-lg font-bold text-red-500">{unhealthy}</div><div className="text-[10px] text-gray-400">Unhealthy</div></div>
      </div>
      <div className="grid grid-cols-2 divide-x dark:divide-gray-700 p-3 text-xs">
        <div>
          <div className="text-gray-400 mb-1">By Team</div>
          {Object.entries(byTeam).map(([t, c]) => <div key={t} className="flex justify-between py-0.5"><span>{t}</span><span className="text-gray-400">{c}</span></div>)}
        </div>
        <div className="pl-3">
          <div className="text-gray-400 mb-1">By Type</div>
          {Object.entries(byType).map(([t, c]) => <div key={t} className="flex justify-between py-0.5"><span>{t}</span><span className="text-gray-400">{c}</span></div>)}
        </div>
      </div>
    </div>
  );
}
