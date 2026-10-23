"use client";

interface TosResult { title: string; description: string; passed: boolean; required: boolean; critical: boolean; }
interface TosComplianceCardProps { results: TosResult[]; compliant: boolean; score: number; }

export function TosComplianceCard({ results, compliant, score }: TosComplianceCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">📜 TOS Compliance</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full ${compliant ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
          {compliant ? "✅ Compliant" : "❌ Non-compliant"} · {score}%
        </span>
      </div>
      <div className="space-y-1.5">
        {results.map(r => (
          <div key={r.title} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <span>{r.passed ? "✅" : r.critical ? "❌" : "⚠️"}</span>
              <span className={r.critical ? "text-red-600 font-medium" : ""}>{r.title}</span>
              {r.required && <span className="text-xs text-gray-400">Required</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
