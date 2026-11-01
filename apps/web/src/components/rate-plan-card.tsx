"use client";

interface RatePlanCardProps { planId: string; rpm: number; rpd: number; burst: number;
  concurrent: number; rpmUsagePct: number; rpdUsagePct: number; throttled: boolean; upgradeSuggested: boolean; }

export function RatePlanCard({ planId, rpm, rpd, burst, concurrent, rpmUsagePct, rpdUsagePct, throttled, upgradeSuggested }: RatePlanCardProps) {
  return (
    <div className={`rounded-xl border p-4 ${throttled ? "border-red-300 dark:border-red-700" : "dark:border-gray-700"}`}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold capitalize">{planId} Plan</h3>
        {throttled && <span className="rounded bg-red-100 px-2 py-0.5 text-xs text-red-700 dark:bg-red-900/30">Throttled</span>}
        {upgradeSuggested && !throttled && <span className="rounded bg-yellow-100 px-2 py-0.5 text-xs text-yellow-700 dark:bg-yellow-900/30">Upgrade?</span>}
      </div>
      <div className="grid grid-cols-2 gap-3 text-center">
        <div><p className="text-lg font-bold">{rpm}</p><p className="text-xs text-gray-400">req/min</p></div>
        <div><p className="text-lg font-bold">{rpd.toLocaleString()}</p><p className="text-xs text-gray-400">req/day</p></div>
        <div><p className="text-lg font-bold">{burst}</p><p className="text-xs text-gray-400">burst</p></div>
        <div><p className="text-lg font-bold">{concurrent}</p><p className="text-xs text-gray-400">concurrent</p></div>
      </div>
      <div className="mt-3 space-y-1">
        <div className="flex justify-between text-xs"><span>RPM</span><span>{rpmUsagePct}%</span></div>
        <div className="h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
          <div className={`h-full rounded-full ${rpmUsagePct > 80 ? "bg-red-500" : "bg-blue-500"}`} style={{ width: `${Math.min(rpmUsagePct, 100)}%` }} />
        </div>
      </div>
    </div>
  );
}
