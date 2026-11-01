"use client";

interface RiskFactor { factor: string; value: number; threshold: number; riskContribution: number; high: boolean; }
interface ChangeRiskCardProps { riskScore: number; riskLevel: string;
  factors: RiskFactor[]; deployCaution: boolean; }

const LEVEL_COLORS: Record<string, string> = {
  low: "text-green-600", medium: "text-yellow-600", high: "text-orange-600", critical: "text-red-600",
};

export function ChangeRiskCard({ riskScore, riskLevel, factors, deployCaution }: ChangeRiskCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 text-center border-b dark:border-gray-700">
        <div className={`text-4xl font-bold ${LEVEL_COLORS[riskLevel] ?? ""}`}>{riskScore}</div>
        <div className="text-xs text-gray-400">Change Risk Score</div>
        <div className={`text-xs mt-1 capitalize ${LEVEL_COLORS[riskLevel] ?? ""}`}>
          {riskLevel} risk {deployCaution ? "⚠ Deploy with caution" : ""}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {factors.map(f => (
          <div key={f.factor} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className={f.high ? "text-red-600" : ""}>{f.factor.replaceAll("_", " ")}</span>
            <span className="text-gray-400">{f.value}/{f.threshold} (+{f.riskContribution})</span>
          </div>
        ))}
      </div>
    </div>
  );
}
