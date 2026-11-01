"use client";

interface DeployCadenceChartProps { total: number; perDay: number; perWeek: number;
  doraLevel: string; busiestDay: string | null; byEnvironment: Record<string, number>; }

const DORA_COLORS: Record<string, string> = {
  elite: "text-green-600", high: "text-blue-600", medium: "text-yellow-600", low: "text-red-600",
};

export function DeployCadenceChart({ total, perDay, perWeek, doraLevel, busiestDay, byEnvironment }: DeployCadenceChartProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚀 Deploy Cadence</h3>
        <span className={`text-xs font-medium ${DORA_COLORS[doraLevel] ?? ""}`}>DORA: {doraLevel}</span>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        <div className="bg-white dark:bg-gray-900 p-3 text-center"><div className="text-lg font-bold">{total}</div><div className="text-[9px] text-gray-400">Total</div></div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center"><div className="text-lg font-bold">{perDay}</div><div className="text-[9px] text-gray-400">Per Day</div></div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center"><div className="text-lg font-bold">{perWeek}</div><div className="text-[9px] text-gray-400">Per Week</div></div>
      </div>
      <div className="p-3 text-xs text-gray-400">
        {busiestDay && `Busiest: ${busiestDay}`} · Envs: {Object.entries(byEnvironment).map(([e, c]) => `${e}: ${c}`).join(", ")}
      </div>
    </div>
  );
}
