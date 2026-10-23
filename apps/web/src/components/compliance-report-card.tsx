"use client";

interface Control { id: string; title: string; status: string; }
interface ComplianceReportCardProps { reportId: string; framework: string;
  score: number; passed: number; failed: number; compliant: boolean;
  controls: Control[]; }

export function ComplianceReportCard({ reportId, framework, score, passed, failed, compliant, controls }: ComplianceReportCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`flex items-center justify-between p-4 border-b dark:border-gray-700 ${compliant ? "bg-green-50 dark:bg-green-900/10" : "bg-red-50 dark:bg-red-900/10"}`}>
        <div>
          <h3 className="font-semibold text-sm">📋 {framework} Report</h3>
          <div className="text-[10px] text-gray-400">{reportId}</div>
        </div>
        <div className="text-right">
          <div className={`text-xl font-bold ${compliant ? "text-green-600" : "text-red-600"}`}>{score}%</div>
          <div className="text-[10px] text-gray-400">{passed}✓ {failed}✗</div>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-48 overflow-y-auto">
        {controls.map(c => (
          <div key={c.id} className="flex items-center justify-between px-4 py-2 text-xs">
            <span>{c.status === "passed" ? "✅" : "❌"} {c.id}: {c.title}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
