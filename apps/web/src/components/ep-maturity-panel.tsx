"use client";
interface EpMaturityPanelProps { endpoint: string; score: number; total: number; pct: number;
  level: string; dimensions: Record<string, number>; }
const LVL_COLOR: Record<string, string> = { mature: "text-green-600", growing: "text-blue-500", basic: "text-yellow-600", initial: "text-red-500" };
export function EpMaturityPanel({ endpoint, score, total, pct, level, dimensions }: EpMaturityPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎯 Maturity: {endpoint}</h3>
        <span className={`text-xs font-bold ${LVL_COLOR[level] ?? ""}`}>
          {level} · {score}/{total} ({pct}%)
        </span>
      </div>
      <div className="p-4 flex flex-wrap gap-1.5">
        {Object.entries(dimensions).map(([dim, met]) => (
          <span key={dim} className={`text-[10px] px-1.5 py-0.5 rounded ${
            met ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300" :
            "bg-gray-100 text-gray-400 dark:bg-gray-800 line-through"}`}>
            {dim.replace("_", " ")}
          </span>
        ))}
      </div>
    </div>
  );
}
