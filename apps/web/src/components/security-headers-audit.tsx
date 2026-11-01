"use client";

interface Finding { header: string; status: string; severity: string; recommendation: string; current?: string; }
interface SecurityHeadersAuditProps { findings: Finding[]; score: number; grade: string;
  present: number; totalRecommended: number; }

const gradeColor: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", F: "text-red-600" };
const statusIcon: Record<string, string> = { missing: "❌", weak: "⚠️" };

export function SecurityHeadersAudit({ findings, score, grade, present, totalRecommended }: SecurityHeadersAuditProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Security Headers</h2>
        <div className="text-right">
          <span className={`text-3xl font-black ${gradeColor[grade] ?? ""}`}>{grade}</span>
          <p className="text-xs text-gray-400">{present}/{totalRecommended} · {score}%</p>
        </div>
      </div>
      {findings.length === 0 ? (
        <p className="text-center text-sm text-green-600">✅ All recommended headers present</p>
      ) : (
        <div className="space-y-1.5">
          {findings.map(f => (
            <div key={f.header} className="rounded border border-yellow-200 px-3 py-2 dark:border-yellow-800">
              <div className="flex items-center gap-2">
                <span>{statusIcon[f.status] ?? "⚠️"}</span>
                <code className="text-xs font-bold">{f.header}</code>
                <span className="text-[10px] text-gray-400">{f.severity}</span>
              </div>
              <p className="mt-0.5 text-xs text-gray-400">→ {f.recommendation}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
