"use client";
interface DeployRiskPanelProps { score: number; level: string; factors: string[]; deployName: string; }
const LVL_COLOR: Record<string, string> = { critical: "bg-red-500", high: "bg-orange-500", medium: "bg-yellow-500", low: "bg-green-500" };
export function DeployRiskPanel({ score, level, factors, deployName }: DeployRiskPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center ${LVL_COLOR[level] ?? "bg-gray-500"}`}>
        <div className="text-2xl font-black">{score}/100</div>
        <div className="text-xs">{level.toUpperCase()} RISK · {deployName}</div>
      </div>
      {factors.length > 0 && (
        <div className="p-3 flex flex-wrap gap-1">
          {factors.map(f => <span key={f} className="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800">{f.replace("_", " ")}</span>)}
        </div>
      )}
    </div>
  );
}
