"use client";

interface LicenseResult { name: string; version: string; license: string; risk: string; commercial: boolean | null; copyleft: boolean | null; }
interface LicenseScanReportProps { dependencies: LicenseResult[]; commercialSafe: boolean;
  hasCritical: boolean; copyleftCount: number; byRisk: Record<string, number>; }

const riskBadge: Record<string, string> = {
  low: "bg-green-100 text-green-700 dark:bg-green-900/30",
  medium: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-900/30",
  critical: "bg-red-100 text-red-700 dark:bg-red-900/30",
  unknown: "bg-gray-100 text-gray-600 dark:bg-gray-800",
};

export function LicenseScanReport({ dependencies, commercialSafe, hasCritical, copyleftCount, byRisk }: LicenseScanReportProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">License Scan</h2>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${commercialSafe && !hasCritical ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {commercialSafe && !hasCritical ? "✅ Commercial Safe" : "⚠️ Review Required"}
        </span>
      </div>
      <div className="flex gap-2">
        {Object.entries(byRisk).map(([risk, count]) => (
          <span key={risk} className={`rounded-full px-2.5 py-0.5 text-xs ${riskBadge[risk] ?? riskBadge.unknown}`}>
            {risk}: {count}
          </span>
        ))}
        {copyleftCount > 0 && (
          <span className="rounded-full bg-purple-100 px-2.5 py-0.5 text-xs text-purple-700 dark:bg-purple-900/30">
            Copyleft: {copyleftCount}
          </span>
        )}
      </div>
      <div className="space-y-1">
        {dependencies.map(d => (
          <div key={d.name} className="flex items-center justify-between rounded border px-3 py-1.5 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm">{d.name}</span>
              <span className="text-xs text-gray-400">{d.version}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs">{d.license}</span>
              <span className={`rounded-full px-1.5 py-0.5 text-[10px] ${riskBadge[d.risk] ?? ""}`}>{d.risk}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
