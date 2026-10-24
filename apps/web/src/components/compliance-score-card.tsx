"use client";

interface ComplianceResult { id: string; label: string; category: string; passed: boolean; }
interface ComplianceScoreCardProps { score: number; results: ComplianceResult[]; compliant: boolean; }

export function ComplianceScoreCard({ score, results, compliant }: ComplianceScoreCardProps) {
  const color = score >= 80 ? "text-green-600" : score >= 50 ? "text-yellow-600" : "text-red-600";
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Compliance</h3>
        <div className="text-right">
          <span className={`text-2xl font-bold ${color}`}>{score}%</span>
          <p className="text-xs text-gray-400">{compliant ? "✅ Compliant" : "⚠️ Issues found"}</p>
        </div>
      </div>
      <ul className="mt-3 space-y-1">
        {results.map(r => (
          <li key={r.id} className="flex items-center gap-2 text-sm">
            <span>{r.passed ? "✅" : "❌"}</span>
            <span className={r.passed ? "text-gray-600 dark:text-gray-400" : "font-medium"}>{r.label}</span>
            <span className="ml-auto text-xs text-gray-400">{r.category}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
