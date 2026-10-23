"use client";

interface Dimension { dimension: string; score: number; weight: number; weighted: number; description: string; }
interface HealthScoreCardProps { overall: number; grade: string; status: string; details: Dimension[]; }

const gradeColors: Record<string, string> = {
  "A+": "text-green-600", A: "text-green-600", B: "text-blue-600",
  C: "text-yellow-600", D: "text-orange-600", F: "text-red-600",
};

export function HealthScoreCard({ overall, grade, status, details }: HealthScoreCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className={`text-4xl font-bold ${gradeColors[grade] ?? ""}`}>{grade}</p>
          <p className="text-sm text-gray-400">{overall}/100 · {status}</p>
        </div>
        <div className="relative h-16 w-16">
          <svg viewBox="0 0 36 36" className="h-full w-full -rotate-90">
            <circle cx="18" cy="18" r="16" fill="none" stroke="currentColor" strokeWidth="2" className="text-gray-200 dark:text-gray-700" />
            <circle cx="18" cy="18" r="16" fill="none" stroke="currentColor" strokeWidth="2"
              strokeDasharray={`${overall} ${100 - overall}`}
              className={overall >= 80 ? "text-green-500" : overall >= 60 ? "text-yellow-500" : "text-red-500"} />
          </svg>
        </div>
      </div>
      <div className="space-y-2">
        {details.map(d => (
          <div key={d.dimension} className="space-y-1">
            <div className="flex justify-between text-sm">
              <span className="capitalize">{d.dimension}</span>
              <span className="text-gray-400">{d.score}/100</span>
            </div>
            <div className="h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
              <div className={`h-full rounded-full ${d.score >= 80 ? "bg-green-500" : d.score >= 60 ? "bg-yellow-500" : "bg-red-500"}`}
                style={{ width: `${d.score}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
