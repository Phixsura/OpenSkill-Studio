"use client";

interface VulnFinding { package_name: string; version: string; cve: string;
  severity: string; fixVersion: string; title: string; }
interface DepVulnReportProps { findings: VulnFinding[]; depsScanned: number;
  critical: number; high: number; clean: boolean; }

const SEV_STYLE: Record<string, string> = {
  critical: "bg-red-100 text-red-700", high: "bg-orange-100 text-orange-700",
  medium: "bg-yellow-100 text-yellow-700", low: "bg-blue-100 text-blue-700",
};

export function DepVulnReport({ findings, depsScanned, critical, high, clean }: DepVulnReportProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🛡️ Vulnerability Scan</h3>
        <span className={`text-xs font-bold ${clean ? "text-green-600" : "text-red-500"}`}>
          {clean ? "✅ Clean" : `⚠ ${critical}C ${high}H`} · {depsScanned} deps
        </span>
      </div>
      {findings.length > 0 ? (
        <div className="divide-y dark:divide-gray-700">
          {findings.map(f => (
            <div key={f.cve} className="px-4 py-2 text-xs">
              <div className="flex justify-between mb-0.5">
                <span className="font-mono">{f.package_name}@{f.version}</span>
                <span className={`px-1 rounded text-[10px] ${SEV_STYLE[f.severity] ?? ""}`}>{f.severity}</span>
              </div>
              <div className="text-gray-400">{f.cve} — {f.title}{f.fixVersion ? ` · fix: ${f.fixVersion}` : ""}</div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 text-xs text-green-600 text-center">No vulnerabilities found</div>
      )}
    </div>
  );
}
