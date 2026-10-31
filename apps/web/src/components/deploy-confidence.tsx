"use client";

interface Check { check: string; weight: number; passed: boolean; }
interface DeployConfidenceProps { confidenceScore: number; riskLevel: string;
  deployRecommended: boolean; checks: Check[]; }

const RISK_COLORS: Record<string, string> = { low: "text-green-600", medium: "text-yellow-600", high: "text-red-600" };

export function DeployConfidence({ confidenceScore, riskLevel, deployRecommended, checks }: DeployConfidenceProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 text-center border-b dark:border-gray-700">
        <div className={`text-4xl font-bold ${RISK_COLORS[riskLevel] ?? ""}`}>{confidenceScore}%</div>
        <div className="text-xs text-gray-400">Deploy Confidence</div>
        <div className={`text-xs mt-1 ${deployRecommended ? "text-green-600" : "text-red-500"}`}>
          {deployRecommended ? "✅ Deploy Recommended" : "🚫 Not Ready"}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {checks.map(c => (
          <div key={c.check} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span>{c.passed ? "✅" : "❌"} {c.check.replaceAll("_", " ")}</span>
            <span className="text-gray-400">{c.weight}pts</span>
          </div>
        ))}
      </div>
    </div>
  );
}
