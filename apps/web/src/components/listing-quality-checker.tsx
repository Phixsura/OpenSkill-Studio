"use client";

interface QualityCheck { field: string; passed: boolean; message: string; }
interface ListingQualityCheckerProps { checks: QualityCheck[]; score: number;
  ready: boolean; passed: number; total: number; }

export function ListingQualityChecker({ checks, score, ready, passed, total }: ListingQualityCheckerProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">✅ Listing Quality</h3>
        <div className="flex items-center gap-2">
          <span className="text-sm font-bold">{score}%</span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${ready ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
            {ready ? "Ready to publish" : `${total - passed} issues`}
          </span>
        </div>
      </div>
      <div className="space-y-1.5">
        {checks.map(c => (
          <div key={c.field} className="flex items-center gap-2 text-sm">
            <span>{c.passed ? "✅" : "❌"}</span>
            <span className={c.passed ? "text-gray-500" : "text-red-600"}>{c.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
