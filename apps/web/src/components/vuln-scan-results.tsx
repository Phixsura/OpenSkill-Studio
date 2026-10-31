"use client";

interface Vuln { package_name: string; cve: string; severity: string; fixedIn: string; }
interface VulnScanResultsProps { vulns: Vuln[]; total: number; hasCritical: boolean;
  riskScore: number; bySeverity: Record<string, number>; }

const SEV_COLORS: Record<string, string> = {
  critical: "bg-red-500 text-white", high: "bg-orange-500 text-white",
  medium: "bg-yellow-400 text-black", low: "bg-blue-400 text-white",
};

export function VulnScanResults({ vulns, total, hasCritical, riskScore, bySeverity }: VulnScanResultsProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Vulnerability Scan</h3>
        <div className="flex gap-2 text-xs">
          <span>{total} vulns</span>
          <span className="text-gray-400">risk: {riskScore}</span>
          {hasCritical && <span className="text-red-500 font-medium">⚠ Critical</span>}
        </div>
      </div>
      <div className="flex gap-2 px-4 py-2 border-b dark:border-gray-700">
        {Object.entries(bySeverity).map(([sev, count]) => (
          <span key={sev} className={`px-2 py-0.5 text-[10px] rounded-full ${SEV_COLORS[sev] ?? ""}`}>
            {sev}: {count}
          </span>
        ))}
      </div>
      <div className="divide-y dark:divide-gray-700">
        {vulns.map((v, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span className={`px-1.5 py-0.5 rounded text-[10px] ${SEV_COLORS[v.severity] ?? ""}`}>{v.severity}</span>
              <span className="font-mono">{v.package_name}</span>
              <span className="text-gray-400">{v.cve}</span>
            </div>
            {v.fixedIn && <span className="text-green-600">→ {v.fixedIn}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
