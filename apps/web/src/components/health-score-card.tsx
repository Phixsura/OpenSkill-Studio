"use client";

interface ScoreBreakdown { raw: number; weight: number; weighted: number; }
interface HealthScoreCardProps { score: number; grade: string; status: string;
  breakdown: Record<string, ScoreBreakdown>; delta?: number; }

const GRADE_COLORS: Record<string, string> = {
  A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-orange-600", F: "text-red-600",
};

export function HealthScoreCard({ score, grade, status, breakdown, delta }: HealthScoreCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-6 text-center border-b dark:border-gray-700">
        <div className={`text-5xl font-bold ${GRADE_COLORS[grade] ?? ""}`}>{grade}</div>
        <div className="text-lg font-mono mt-1">{score}/100</div>
        <div className="text-xs text-gray-400 capitalize">{status}</div>
        {delta !== undefined && (
          <div className={`text-xs mt-1 ${delta >= 0 ? "text-green-600" : "text-red-500"}`}>
            {delta >= 0 ? "↑" : "↓"} {Math.abs(delta)} pts
          </div>
        )}
      </div>
      <div className="p-4 space-y-2">
        {Object.entries(breakdown).map(([key, b]) => (
          <div key={key}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className="capitalize">{key.replaceAll("_", " ")}</span>
              <span className="text-gray-400">{b.raw} × {b.weight} = {b.weighted}</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className="h-full bg-blue-500 rounded-full" style={{ width: `${b.raw}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
