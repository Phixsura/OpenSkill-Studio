"use client";

interface DataAccess { resource: string; access: string; }
interface PrivacyOverviewCardProps { dataAccess: DataAccess[]; networkHosts: string[]; sandboxed: boolean;
  secretsCount: number; privacyUrl: string | null; riskLevel: string; }

const RISK_COLORS: Record<string, string> = { low: "text-green-600", medium: "text-yellow-600", high: "text-red-600" };

export function PrivacyOverviewCard({ dataAccess, networkHosts, sandboxed, secretsCount, privacyUrl, riskLevel }: PrivacyOverviewCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="font-semibold">🔒 Privacy</h4>
        <span className={`text-sm font-medium capitalize ${RISK_COLORS[riskLevel] ?? ""}`}>{riskLevel} risk</span>
      </div>
      <div className="space-y-2 text-sm">
        <p>{sandboxed ? "✅ Sandboxed" : "⚠️ Not sandboxed"}</p>
        <p>📊 Accesses {dataAccess.length} resource{dataAccess.length !== 1 ? "s" : ""}</p>
        <p>🌐 {networkHosts.length > 0 ? `${networkHosts.length} external host${networkHosts.length !== 1 ? "s" : ""}` : "No network access"}</p>
        <p>🔐 {secretsCount} secret{secretsCount !== 1 ? "s" : ""} stored</p>
        {privacyUrl && /^https?:/.test(privacyUrl) ? <a href={privacyUrl} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Privacy Policy →</a> : <p className="text-yellow-600">⚠️ No privacy policy</p>}
      </div>
    </div>
  );
}
