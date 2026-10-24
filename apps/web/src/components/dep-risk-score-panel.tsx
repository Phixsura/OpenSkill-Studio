"use client";
interface RiskScore { service: string; score: number; level: string; }
interface DepRiskScorePanelProps { services: RiskScore[]; }
const LEVEL_COLOR: Record<string, string> = { critical: "text-red-600", high: "text-orange-500", medium: "text-yellow-600", low: "text-green-600" };
export function DepRiskScorePanel({ services }: DepRiskScorePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚠️ Dependency Risk</h3>
        <span className="text-xs text-gray-400">{services.length} services scored</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.service} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{s.service}</span>
            <div className="flex items-center gap-2">
              <span className="text-gray-400">score: {s.score}</span>
              <span className={`font-bold ${LEVEL_COLOR[s.level] ?? ""}`}>{s.level}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
