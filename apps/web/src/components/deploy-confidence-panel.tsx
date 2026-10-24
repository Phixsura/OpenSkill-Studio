"use client";
interface DeployConfidencePanelProps { score: number; level: string; factors: Record<string, number>; }
const LVL_STYLE: Record<string, string> = { high: "bg-green-500", medium: "bg-yellow-500", low: "bg-red-500" };
export function DeployConfidencePanel({ score, level, factors }: DeployConfidencePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-4 text-white text-center ${LVL_STYLE[level] ?? "bg-gray-500"}`}>
        <div className="text-3xl font-black">{score}/100</div>
        <div className="text-sm">{level.toUpperCase()} CONFIDENCE</div>
      </div>
      <div className="p-4 space-y-1.5">
        {Object.entries(factors).map(([k, v]) => (
          <div key={k} className="flex items-center gap-2 text-xs">
            <span className="w-16 text-gray-500 capitalize">{k}</span>
            <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className="h-full bg-blue-500 rounded-full" style={{ width: `${v * 4}%` }} />
            </div>
            <span className="w-6 text-right text-gray-400">{v}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
