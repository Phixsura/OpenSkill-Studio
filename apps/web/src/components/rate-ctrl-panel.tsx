"use client";
interface RateCtrlPanelProps { currentLimit: number; currentRps: number; headroomPct: number; action: string; }
const ACTION_COLOR: Record<string, string> = { reduce: "text-red-500", increase: "text-green-600", maintain: "text-gray-400" };
export function RateCtrlPanel({ currentLimit, currentRps, headroomPct, action }: RateCtrlPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎛️ Rate Controller</h3>
        <span className={`text-xs font-bold ${ACTION_COLOR[action] ?? ""}`}>
          {action} · limit: {currentLimit.toLocaleString()} rps
        </span>
      </div>
      <div className="p-4">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-gray-400">{currentRps.toLocaleString()} rps</span>
          <span className="text-gray-400">{headroomPct}% headroom</span>
        </div>
        <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full">
          <div className={`h-full rounded-full ${headroomPct < 20 ? "bg-red-500" : headroomPct < 50 ? "bg-yellow-500" : "bg-green-500"}`}
            style={{ width: `${100 - headroomPct}%` }} />
        </div>
      </div>
    </div>
  );
}
