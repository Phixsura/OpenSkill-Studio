"use client";

interface DbConnStatsPanelProps { active: number; idle: number; max: number;
  waiting: number; utilizationPct: number; health: string;
  recommendations: string[]; }

export function DbConnStatsPanel({ active, idle, max, waiting, utilizationPct, health, recommendations }: DbConnStatsPanelProps) {
  const healthColor = health === "healthy" ? "text-green-600" : health === "busy" ? "text-yellow-600" : "text-red-600";
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔌 DB Connections</h3>
        <span className={`text-xs font-medium ${healthColor}`}>{health} · {utilizationPct}%</span>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        {[{ l: "Active", v: active }, { l: "Idle", v: idle },
          { l: "Max", v: max }, { l: "Waiting", v: waiting }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
      {recommendations.length > 0 && (
        <div className="p-3">
          {recommendations.map((r, i) => <div key={i} className="text-xs text-yellow-600 py-0.5">💡 {r}</div>)}
        </div>
      )}
    </div>
  );
}
