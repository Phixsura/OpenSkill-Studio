"use client";

interface FrameworkResult { passed: number; total: number; pct: number; compliant: boolean; }
interface ComplianceTrackerProps { frameworks: Record<string, FrameworkResult>;
  overallPct: number; allCompliant: boolean; }

export function ComplianceTracker({ frameworks, overallPct, allCompliant }: ComplianceTrackerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏛️ Compliance Tracker</h3>
        <div className="flex gap-2 text-xs">
          <span className="font-bold">{overallPct}%</span>
          <span className={allCompliant ? "text-green-600" : "text-yellow-600"}>
            {allCompliant ? "✅ All Compliant" : "⚠ Gaps Found"}
          </span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {Object.entries(frameworks).map(([name, data]) => (
          <div key={name} className="px-4 py-2.5">
            <div className="flex justify-between text-xs mb-0.5">
              <span className="font-medium">{data.compliant ? "✅" : "⚠"} {name}</span>
              <span className="text-gray-400">{data.passed}/{data.total} ({data.pct}%)</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${data.compliant ? "bg-green-500" : "bg-yellow-500"}`}
                style={{ width: `${data.pct}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
