"use client";

interface Permission { scope: string; label: string; risk: string; category: string; }
interface PermissionRiskCardProps { permissions: Permission[]; overallRisk: string; requiresReview: boolean; }

const RISK_COLORS: Record<string, string> = {
  low: "text-green-600", medium: "text-yellow-600", high: "text-orange-600", critical: "text-red-600",
};
const RISK_BADGES: Record<string, string> = {
  low: "bg-green-100 text-green-700", medium: "bg-yellow-100 text-yellow-700",
  high: "bg-orange-100 text-orange-700", critical: "bg-red-100 text-red-700",
};

export function PermissionRiskCard({ permissions, overallRisk, requiresReview }: PermissionRiskCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Permissions</h3>
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${RISK_BADGES[overallRisk] || ""}`}>
          {overallRisk} risk
        </span>
      </div>
      {requiresReview && (
        <p className="mt-2 text-xs text-red-600">⚠️ Requires admin review</p>
      )}
      <ul className="mt-3 space-y-1">
        {permissions.map(p => (
          <li key={p.scope} className="flex items-center justify-between text-sm">
            <span>{p.label}</span>
            <span className={`text-xs ${RISK_COLORS[p.risk] || ""}`}>{p.risk}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
