"use client";

interface SignalInfo {
  name: string;
  value: number;
  score: number;
  status: "ok" | "degraded" | "critical";
}

interface HealthScoreCardProps {
  overallScore: number;
  grade: string;
  signals: SignalInfo[];
  appName: string;
}

const GRADE_COLORS: Record<string, string> = {
  A: "text-green-600 dark:text-green-400",
  B: "text-blue-600 dark:text-blue-400",
  C: "text-yellow-600 dark:text-yellow-400",
  D: "text-orange-600 dark:text-orange-400",
  F: "text-red-600 dark:text-red-400",
};

const STATUS_DOTS: Record<string, string> = {
  ok: "bg-green-500",
  degraded: "bg-yellow-500",
  critical: "bg-red-500",
};

export default function HealthScoreCard({
  overallScore,
  grade,
  signals,
  appName,
}: HealthScoreCardProps) {
  const gradeColor = GRADE_COLORS[grade] ?? GRADE_COLORS.F;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Health Score</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className={`text-2xl font-bold ${gradeColor}`}>{grade}</span>
          <p className="text-[11px] text-gray-400">{overallScore}/100</p>
        </div>
      </div>

      <div className="space-y-2">
        {signals.map((s) => (
          <div key={s.name} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span
                className={`h-2 w-2 rounded-full ${STATUS_DOTS[s.status] ?? STATUS_DOTS.critical}`}
              />
              <span className="text-xs capitalize text-gray-700 dark:text-gray-300">
                {s.name.replace("_", " ")}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-1.5 w-16 rounded-full bg-gray-200 dark:bg-gray-700">
                <div
                  className={`h-1.5 rounded-full ${STATUS_DOTS[s.status]}`}
                  style={{ width: `${Math.min(s.score, 100)}%` }}
                />
              </div>
              <span className="w-8 text-right text-[11px] text-gray-500">{s.score.toFixed(0)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
