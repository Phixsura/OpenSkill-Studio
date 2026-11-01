"use client";

interface DependencyAuditCardProps { total: number; vulnCount: number; outdatedCount: number; score: number; grade: string; }

export function DependencyAuditCard({ total, vulnCount, outdatedCount, score, grade }: DependencyAuditCardProps) {
  const gradeColors: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", F: "text-red-600" };
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Dependency Audit</h3>
        <span className={`text-xl font-bold ${gradeColors[grade] || ""}`}>{grade}</span>
      </div>
      <div className="mt-3 grid grid-cols-3 gap-3 text-center">
        <div><p className="text-lg font-bold">{total}</p><p className="text-xs text-gray-400">Total</p></div>
        <div><p className={`text-lg font-bold ${vulnCount > 0 ? "text-red-600" : "text-green-600"}`}>{vulnCount}</p><p className="text-xs text-gray-400">Vulns</p></div>
        <div><p className={`text-lg font-bold ${outdatedCount > 0 ? "text-yellow-600" : ""}`}>{outdatedCount}</p><p className="text-xs text-gray-400">Outdated</p></div>
      </div>
      <div className="mt-2 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-full rounded-full ${score >= 80 ? "bg-green-500" : score >= 50 ? "bg-yellow-500" : "bg-red-500"}`}
          style={{ width: `${score}%` }} />
      </div>
    </div>
  );
}
