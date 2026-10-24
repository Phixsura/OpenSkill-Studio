"use client";

interface RolloutRiskCardProps { riskScore: number; riskLevel: string;
  riskFactors: string[]; recommendCanary: boolean; }

const LEVEL_COLORS: Record<string, string> = {
  low: "text-green-600", medium: "text-yellow-600", high: "text-orange-600", critical: "text-red-600",
};

export function RolloutRiskCard({ riskScore, riskLevel, riskFactors, recommendCanary }: RolloutRiskCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 text-center border-b dark:border-gray-700">
        <div className={`text-3xl font-bold ${LEVEL_COLORS[riskLevel] ?? ""}`}>{riskScore}</div>
        <div className="text-xs text-gray-400">Rollout Risk · {riskLevel}</div>
        {recommendCanary && <div className="text-[10px] text-yellow-600 mt-1">🐤 Canary deploy recommended</div>}
      </div>
      {riskFactors.length > 0 && (
        <div className="p-3">
          {riskFactors.map(f => (
            <div key={f} className="text-xs text-gray-500 py-0.5">⚠ {f.replaceAll("_", " ")}</div>
          ))}
        </div>
      )}
    </div>
  );
}
