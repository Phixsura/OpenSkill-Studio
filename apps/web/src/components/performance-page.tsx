"use client";

interface Vital { name: string; display: string; threshold: string; score: string; description: string; }
interface PerformancePageProps { vitals: Vital[]; overall: string; overallLabel: string; }

const scoreColors: Record<string, string> = {
  good: "text-green-600 bg-green-50 dark:bg-green-900/10",
  needs_improvement: "text-yellow-600 bg-yellow-50 dark:bg-yellow-900/10",
  poor: "text-red-600 bg-red-50 dark:bg-red-900/10",
};

export function PerformancePage({ vitals, overall, overallLabel }: PerformancePageProps) {
  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">⚡ Performance</h2>
        <span className={`rounded-lg px-3 py-1 text-sm font-medium ${scoreColors[overall] ?? ""}`}>{overallLabel}</span>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        {vitals.map(v => (
          <div key={v.name} className={`rounded-xl border p-4 ${scoreColors[v.score] ?? ""} dark:border-gray-700`}>
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold">{v.name}</h3>
              <span className="text-xl font-bold">{v.display}</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">{v.description}</p>
            <p className="text-xs text-gray-400 mt-0.5">Target: {v.threshold}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
