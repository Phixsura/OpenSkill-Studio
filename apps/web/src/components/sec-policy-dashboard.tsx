"use client";

interface Violation { policy: string; description: string; severity: string; }
interface SecPolicyDashboardProps { resourceName: string; compliant: boolean;
  violations: Violation[]; riskLevel: string; riskScore: number; }

const SEV_COLORS: Record<string, string> = {
  critical: "bg-red-500 text-white", high: "bg-orange-500 text-white",
  medium: "bg-yellow-400 text-black", low: "bg-blue-400 text-white",
};

export function SecPolicyDashboard({ resourceName, compliant, violations, riskLevel, riskScore }: SecPolicyDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`flex items-center justify-between p-4 border-b dark:border-gray-700 ${compliant ? "bg-green-50 dark:bg-green-900/10" : "bg-red-50 dark:bg-red-900/10"}`}>
        <div>
          <h3 className="font-semibold text-sm">🛡️ Security: {resourceName}</h3>
          <div className="text-[10px] text-gray-400">Risk: {riskLevel} (score {riskScore})</div>
        </div>
        <span className={`text-xs font-medium ${compliant ? "text-green-600" : "text-red-500"}`}>
          {compliant ? "✅ Compliant" : `⚠ ${violations.length} violations`}
        </span>
      </div>
      {violations.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {violations.map(v => (
            <div key={v.policy} className="flex items-center justify-between px-4 py-2 text-xs">
              <div>
                <span className="font-medium">{v.policy}</span>
                <span className="text-gray-400 ml-2">{v.description}</span>
              </div>
              <span className={`px-1.5 py-0.5 text-[10px] rounded ${SEV_COLORS[v.severity] ?? ""}`}>{v.severity}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
