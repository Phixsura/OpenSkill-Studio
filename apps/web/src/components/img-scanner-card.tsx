"use client";

interface ImgScanResult { image: string; sizeMb: number; vulns: number;
  critical: number; high: number; pass: boolean; issues: string[]; }
interface ImgScannerCardProps { results: ImgScanResult[]; passRate: number;
  totalImages: number; totalVulns: number; }

export function ImgScannerCard({ results, passRate, totalImages, totalVulns }: ImgScannerCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🐳 Image Scanner</h3>
        <span className="text-xs text-gray-400">{totalImages} images · {passRate}% pass · {totalVulns} vulns</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.image} className="px-4 py-2 text-xs">
            <div className="flex justify-between">
              <span className={`font-mono ${r.pass ? "" : "text-red-600"}`}>{r.pass ? "✅" : "❌"} {r.image}</span>
              <span className="text-gray-400">{r.sizeMb}MB · {r.vulns} vulns ({r.critical}C/{r.high}H)</span>
            </div>
            {r.issues.length > 0 && r.issues.map((issue, i) => (
              <div key={i} className="text-[10px] text-yellow-600 mt-0.5">💡 {issue}</div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
