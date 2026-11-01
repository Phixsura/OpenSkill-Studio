"use client";

interface HealthCheck { metric: string; value: string; score: number; max: number; }
interface AppHealthBadgeProps { score: number; grade: string; checks: HealthCheck[]; }

const GRADE_COLOR: Record<string, string> = {
  A: "bg-green-500", B: "bg-blue-500", C: "bg-yellow-500", D: "bg-red-500",
};

export function AppHealthBadge({ score, grade, checks }: AppHealthBadgeProps) {
  return (
    <div className="rounded-xl border p-4 dark:border-gray-700">
      <div className="flex items-center gap-3 mb-3">
        <div className={`w-10 h-10 rounded-full ${GRADE_COLOR[grade] || "bg-gray-400"} text-white font-bold text-lg flex items-center justify-center`}>{grade}</div>
        <div>
          <p className="text-sm font-bold">{score}/100</p>
          <p className="text-xs text-gray-400">App Health</p>
        </div>
      </div>
      <div className="space-y-1">
        {checks.map(c => (
          <div key={c.metric} className="flex items-center justify-between text-xs">
            <span>{c.metric}: {c.value}</span>
            <span className="text-gray-400">{c.score}/{c.max}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
