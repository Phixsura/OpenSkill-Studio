"use client";

interface Finding { practice: string; description: string; }
interface ConfigAuditCardProps { service: string; score: number; total: number;
  compliancePct: number; grade: string; findings: Finding[]; }

const GRADE_COLORS: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-red-600" };

export function ConfigAuditCard({ service, score, total, compliancePct, grade, findings }: ConfigAuditCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔧 Config Audit: {service}</h3>
        <div className="flex gap-2">
          <span className={`text-lg font-bold ${GRADE_COLORS[grade] ?? ""}`}>{grade}</span>
          <span className="text-xs text-gray-400 self-end">{score}/{total} ({compliancePct}%)</span>
        </div>
      </div>
      {findings.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {findings.map(f => (
            <div key={f.practice} className="px-4 py-1.5 text-xs">
              <span className="text-yellow-600">⚠ {f.practice.replaceAll("_", " ")}</span>
              <span className="text-gray-400 ml-2">— {f.description}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
