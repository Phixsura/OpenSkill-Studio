"use client";

interface DeployFreqCardProps { frequency: string; deploysPerDay: number;
  total: number; periodDays: number; byEnv: Record<string, number>; }

const FREQ_BADGE: Record<string, string> = {
  on_demand: "bg-green-100 text-green-700", weekly: "bg-blue-100 text-blue-700",
  monthly: "bg-yellow-100 text-yellow-700", rare: "bg-red-100 text-red-700",
};

export function DeployFreqCard({ frequency, deploysPerDay, total, periodDays, byEnv }: DeployFreqCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚀 Deploy Frequency</h3>
        <span className={`text-xs px-2 py-0.5 rounded ${FREQ_BADGE[frequency] ?? ""}`}>{frequency}</span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><div className="text-gray-400">Per Day</div><div className="font-bold text-lg">{deploysPerDay}</div></div>
        <div><div className="text-gray-400">Total</div><div className="font-bold text-lg">{total}</div></div>
        <div><div className="text-gray-400">Period</div><div className="font-bold text-lg">{periodDays}d</div></div>
      </div>
      <div className="border-t dark:border-gray-700 p-3 flex gap-3 text-xs">
        {Object.entries(byEnv).map(([env, count]) => (
          <span key={env} className="text-gray-400">{env}: {count}</span>
        ))}
      </div>
    </div>
  );
}
