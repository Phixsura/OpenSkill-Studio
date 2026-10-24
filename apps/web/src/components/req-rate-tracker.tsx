"use client";

interface ReqRateTrackerProps { totalRps: number; errorPct: number; errorRps: number;
  successRps: number; byEndpoint: Record<string, number>; }

export function ReqRateTracker({ totalRps, errorPct, errorRps, successRps, byEndpoint }: ReqRateTrackerProps) {
  const maxRps = Math.max(...Object.values(byEndpoint), 1);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Request Rates</h3>
        <span className="text-xs text-gray-400">{totalRps.toLocaleString()} RPS · {errorPct}% errors</span>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        <div className="bg-white dark:bg-gray-900 p-2 text-center"><div className="text-sm font-bold">{totalRps}</div><div className="text-[9px] text-gray-400">Total</div></div>
        <div className="bg-white dark:bg-gray-900 p-2 text-center"><div className="text-sm font-bold text-green-600">{successRps}</div><div className="text-[9px] text-gray-400">Success</div></div>
        <div className="bg-white dark:bg-gray-900 p-2 text-center"><div className="text-sm font-bold text-red-500">{errorRps}</div><div className="text-[9px] text-gray-400">Errors</div></div>
      </div>
      <div className="p-3 space-y-1.5">
        {Object.entries(byEndpoint).map(([ep, rps]) => (
          <div key={ep}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className="font-mono">{ep}</span><span className="text-gray-400">{rps} rps</span>
            </div>
            <div className="w-full h-1 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className="h-full bg-blue-500 rounded-full" style={{ width: `${(rps / maxRps) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
