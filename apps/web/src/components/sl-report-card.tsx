"use client";

interface SloResult { name: string; actual: number; target: number; met: boolean; budgetRemainingPct: number; }
interface SlReportCardProps { slos: SloResult[]; compliancePct: number;
  met: number; failed: number; grade: string; period: string; }

const GRADE_COLORS: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600" };

export function SlReportCard({ slos, compliancePct, met, failed, grade, period }: SlReportCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold">📊 Service Level Report</h3>
          <div className="text-[10px] text-gray-400">{period}</div>
        </div>
        <div className="text-right">
          <span className={`text-2xl font-bold ${GRADE_COLORS[grade] ?? ""}`}>{grade}</span>
          <div className="text-[10px] text-gray-400">{compliancePct}% · {met}/{met + failed}</div>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {slos.map(s => (
          <div key={s.name} className="flex items-center justify-between px-4 py-2">
            <span className="text-xs">{s.met ? "✅" : "❌"} {s.name}</span>
            <span className="text-xs font-mono">{s.actual}% / {s.target}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
