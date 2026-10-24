"use client";
interface RatePlanPanelProps { plan: string; dailyPct: number; monthlyPct: number;
  exceeded: boolean; recommendUpgrade: boolean; rpm: number; }
export function RatePlanPanel({ plan, dailyPct, monthlyPct, exceeded, recommendUpgrade, rpm }: RatePlanPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Rate Plan</h3>
        <span className={`text-xs font-bold uppercase ${exceeded ? "text-red-500" : "text-green-600"}`}>
          {plan} · {rpm} rpm
        </span>
      </div>
      <div className="p-4 space-y-2">
        <div><div className="flex justify-between text-xs mb-0.5"><span className="text-gray-400">Daily</span><span>{dailyPct}%</span></div>
          <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
            <div className={`h-full rounded-full ${dailyPct > 90 ? "bg-red-500" : dailyPct > 70 ? "bg-yellow-500" : "bg-green-500"}`} style={{ width: `${Math.min(dailyPct, 100)}%` }} /></div></div>
        <div><div className="flex justify-between text-xs mb-0.5"><span className="text-gray-400">Monthly</span><span>{monthlyPct}%</span></div>
          <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
            <div className={`h-full rounded-full ${monthlyPct > 90 ? "bg-red-500" : monthlyPct > 70 ? "bg-yellow-500" : "bg-green-500"}`} style={{ width: `${Math.min(monthlyPct, 100)}%` }} /></div></div>
      </div>
      {recommendUpgrade && <div className="px-4 pb-3 text-xs text-yellow-600">⬆ Consider upgrading your plan</div>}
    </div>
  );
}
