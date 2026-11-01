"use client";

interface Strategy { name: string; description: string; downtime: boolean;
  rollbackSpeed: string; complexity: string; }
interface DeployStrategyPickerProps { strategies: Strategy[]; recommended: string;
  onSelect: (name: string) => void; }

const COMPLEXITY_COLORS: Record<string, string> = {
  low: "bg-green-100 text-green-700", medium: "bg-yellow-100 text-yellow-700",
  high: "bg-red-100 text-red-700",
};

export function DeployStrategyPicker({ strategies, recommended, onSelect }: DeployStrategyPickerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎯 Deploy Strategy</h3>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {strategies.map(s => (
          <button key={s.name} onClick={() => onSelect(s.name)}
            className={`w-full text-left px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800 ${s.name === recommended ? "bg-blue-50 dark:bg-blue-900/10" : ""}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium capitalize">{s.name.replaceAll("_", " ")}</span>
                {s.name === recommended && <span className="text-[10px] text-blue-500">★ recommended</span>}
              </div>
              <span className={`px-1.5 py-0.5 text-[10px] rounded ${COMPLEXITY_COLORS[s.complexity] ?? ""}`}>{s.complexity}</span>
            </div>
            <div className="text-xs text-gray-400 mt-0.5">{s.description}</div>
            <div className="flex gap-3 text-[10px] text-gray-400 mt-1">
              <span>{s.downtime ? "⚠ Downtime" : "✅ Zero-downtime"}</span>
              <span>Rollback: {s.rollbackSpeed}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
