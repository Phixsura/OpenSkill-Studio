"use client";

interface TrainService { service: string; version: string; status: string; owner: string; }
interface ReleaseTrainBoardProps { name: string; targetDate: string; services: TrainService[];
  pctReady: number; allReady: boolean; }

const STATUS_COLORS: Record<string, string> = {
  ready: "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400",
  pending: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400",
  blocked: "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400",
  testing: "bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400",
};

export function ReleaseTrainBoard({ name, targetDate, services, pctReady, allReady }: ReleaseTrainBoardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold text-sm">🚂 {name}</h3>
          <div className="text-xs text-gray-400 mt-0.5">Target: {targetDate}</div>
        </div>
        <div className="text-right">
          <div className={`text-sm font-bold ${allReady ? "text-green-600" : "text-yellow-600"}`}>{pctReady}%</div>
          <div className="text-[10px] text-gray-400">{allReady ? "🚀 Ready" : "In Progress"}</div>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.service} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <span className="text-sm font-medium">{s.service}</span>
              <span className="text-xs text-gray-400 ml-2">v{s.version}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">{s.owner}</span>
              <span className={`px-2 py-0.5 text-[10px] rounded-full ${STATUS_COLORS[s.status] ?? ""}`}>{s.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
