"use client";

interface SecurityOverviewCardProps { score: number; grade: string; critical: number; high: number; needsAttention: boolean; }

export function SecurityOverviewCard({ score, grade, critical, high, needsAttention }: SecurityOverviewCardProps) {
  const gradeColors: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", F: "text-red-600" };
  return (
    <div className={`rounded-lg border p-6 ${needsAttention ? "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/10" : "border-gray-200 dark:border-gray-700"}`}>
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold">Security Score</h3>
          <p className="mt-1 text-xs text-gray-400">Based on scan, dependencies, and policies</p>
        </div>
        <div className="text-right">
          <span className={`text-4xl font-bold ${gradeColors[grade] || ""}`}>{grade}</span>
          <p className="text-sm text-gray-400">{score}/100</p>
        </div>
      </div>
      {needsAttention && (
        <div className="mt-4 flex gap-4 text-sm">
          {critical > 0 && <span className="text-red-600">🔴 {critical} critical</span>}
          {high > 0 && <span className="text-orange-600">🟠 {high} high</span>}
        </div>
      )}
    </div>
  );
}
