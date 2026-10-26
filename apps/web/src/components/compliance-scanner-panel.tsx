"use client";

interface Check { name: string; level: "pass" | "warn" | "fail"; message: string; category: string; }
interface Report { score: number; passed: boolean; checks: Check[]; }

const levelCfg: Record<string, { icon: string; color: string }> = {
  pass: { icon: "✅", color: "" }, warn: { icon: "⚠️", color: "text-yellow-600" },
  fail: { icon: "❌", color: "text-red-600" },
};

export function ComplianceScannerPanel({ report, onScan }: { report: Report | null; onScan?: () => void }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔍 Compliance Scanner</h2>
        <div className="flex items-center gap-2">
          {report && <span className={`text-lg font-bold ${report.passed ? "text-green-600" : "text-red-600"}`}>{report.score}/100</span>}
          <button onClick={onScan} className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg">Scan</button>
        </div>
      </div>
      {report && (
        <div className="space-y-0.5">
          {report.checks.map((c, i) => {
            const cfg = levelCfg[c.level];
            return (
              <div key={i} className="rounded-lg border dark:border-gray-700 p-2 flex items-center gap-2 text-sm">
                <span>{cfg.icon}</span>
                <span className={cfg.color}>{c.message}</span>
                <span className="text-xs text-gray-400 ml-auto">{c.category}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
