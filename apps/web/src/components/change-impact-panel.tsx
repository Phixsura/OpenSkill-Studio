"use client";
interface ChangeImpactPanelProps { score: number; risk: string; factors: string[]; endpoint: string; }
const RISK_STYLE: Record<string, string> = { critical: "bg-red-500", high: "bg-orange-500", medium: "bg-yellow-500", low: "bg-green-500" };
export function ChangeImpactPanel({ score, risk, factors, endpoint }: ChangeImpactPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center ${RISK_STYLE[risk] ?? "bg-gray-500"}`}>
        <div className="text-2xl font-black">{score}/100</div>
        <div className="text-sm">{risk.toUpperCase()} impact · {endpoint}</div>
      </div>
      <div className="p-3 flex flex-wrap gap-1">
        {factors.map(f => (
          <span key={f} className="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800">{f.replace("_", " ")}</span>
        ))}
      </div>
    </div>
  );
}
