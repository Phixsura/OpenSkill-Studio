"use client";

interface Vuln { package_name: string; cve: string; severity: string; fixedIn: string; }
interface DepSecScanProps { totalDeps: number; safe: number; vulnerable: number;
  totalVulns: number; critical: number; high: number; pass: boolean; vulns: Vuln[]; }

const SEV_COLORS: Record<string, string> = {
  critical: "bg-red-500 text-white", high: "bg-orange-500 text-white",
  medium: "bg-yellow-400", low: "bg-blue-400 text-white",
};

export function DepSecScan({ totalDeps, safe, vulnerable, totalVulns, critical, high, pass, vulns }: DepSecScanProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`flex items-center justify-between p-4 border-b dark:border-gray-700 ${pass ? "bg-green-50 dark:bg-green-900/10" : "bg-red-50 dark:bg-red-900/10"}`}>
        <h3 className="font-semibold">🔍 Dependency Security</h3>
        <span className={`text-xs ${pass ? "text-green-600" : "text-red-500"}`}>
          {pass ? "✅ Pass" : `⚠ ${totalVulns} vulns (${critical}C/${high}H)`}
        </span>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        <div className="bg-white dark:bg-gray-900 p-2 text-center"><div className="text-sm font-bold">{totalDeps}</div><div className="text-[9px] text-gray-400">Total</div></div>
        <div className="bg-white dark:bg-gray-900 p-2 text-center"><div className="text-sm font-bold text-green-600">{safe}</div><div className="text-[9px] text-gray-400">Safe</div></div>
        <div className="bg-white dark:bg-gray-900 p-2 text-center"><div className="text-sm font-bold text-red-500">{vulnerable}</div><div className="text-[9px] text-gray-400">Vulnerable</div></div>
      </div>
      {vulns.length > 0 && (
        <div className="divide-y dark:divide-gray-700 max-h-32 overflow-y-auto">
          {vulns.map((v, i) => (
            <div key={i} className="flex justify-between px-4 py-1.5 text-xs">
              <div className="flex gap-2">
                <span className={`px-1 py-0.5 text-[10px] rounded ${SEV_COLORS[v.severity] ?? ""}`}>{v.severity}</span>
                <span className="font-mono">{v.package_name}</span>
              </div>
              <span className="text-gray-400">{v.cve}{v.fixedIn ? ` → ${v.fixedIn}` : ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
