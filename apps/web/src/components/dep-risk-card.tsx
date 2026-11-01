"use client";

interface DepRiskCardProps { service: string; directDeps: number; transitiveDeps: number;
  maxDepth: number; riskScore: number; riskLevel: string; }

const RISK_COLORS: Record<string, string> = {
  low: "text-green-600", medium: "text-yellow-600", high: "text-orange-600", critical: "text-red-600",
};

export function DepRiskCard({ service, directDeps, transitiveDeps, maxDepth, riskScore, riskLevel }: DepRiskCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold text-sm">⚠️ Dependency Risk: {service}</h3>
        <span className={`text-xs font-medium ${RISK_COLORS[riskLevel] ?? ""}`}>
          {riskLevel} ({riskScore}/100)
        </span>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700">
        <div className="bg-white dark:bg-gray-900 p-3 text-center"><div className="text-lg font-bold">{directDeps}</div><div className="text-[9px] text-gray-400">Direct</div></div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center"><div className="text-lg font-bold">{transitiveDeps}</div><div className="text-[9px] text-gray-400">Transitive</div></div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center"><div className="text-lg font-bold">{maxDepth}</div><div className="text-[9px] text-gray-400">Max Depth</div></div>
      </div>
    </div>
  );
}
