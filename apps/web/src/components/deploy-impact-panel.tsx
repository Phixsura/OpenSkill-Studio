"use client";
interface DeployImpactPanelProps { servicesAffected: string[]; impactPct: number;
  usersAffected: number; risk: string; riskFactors: string[]; env: string; requireApproval: boolean; }
const RISK_STYLE: Record<string, string> = { high: "bg-red-500", medium: "bg-yellow-500", low: "bg-green-500" };
export function DeployImpactPanel({ servicesAffected, impactPct, usersAffected, risk, riskFactors, env, requireApproval }: DeployImpactPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center text-sm font-bold ${RISK_STYLE[risk] ?? "bg-gray-500"}`}>
        {risk.toUpperCase()} RISK — {env} — {impactPct}% blast radius — {usersAffected.toLocaleString()} users
      </div>
      <div className="p-4 text-xs space-y-2">
        <div><span className="text-gray-400">Services:</span> {servicesAffected.join(", ")}</div>
        {riskFactors.length > 0 && (
          <div><span className="text-gray-400">Factors:</span> {riskFactors.map(f => f.replace(/_/g, " ")).join(", ")}</div>
        )}
        {requireApproval && <div className="text-yellow-600 font-bold">⚠ Approval required</div>}
      </div>
    </div>
  );
}
