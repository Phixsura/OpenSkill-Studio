"use client";

interface HealthResult { score: number; grade: string; breakdown: Record<string, number>; }

const gradeColors: Record<string, string> = {
  A: "bg-green-500", B: "bg-blue-500", C: "bg-yellow-500", D: "bg-orange-500", F: "bg-red-500",
};

export function HealthScoreBadge({ result, showBreakdown }: { result: HealthResult; showBreakdown?: boolean }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <div className={`w-14 h-14 rounded-xl ${gradeColors[result.grade] || "bg-gray-500"} flex items-center justify-center text-white`}>
          <div className="text-center">
            <span className="text-xl font-extrabold block leading-none">{result.grade}</span>
            <span className="text-[10px]">{result.score}</span>
          </div>
        </div>
        <div>
          <span className="font-bold text-sm block">Health Score</span>
          <span className="text-xs text-gray-500">{result.score}/100 points</span>
        </div>
      </div>
      {showBreakdown && (
        <div className="space-y-1">
          {Object.entries(result.breakdown).map(([key, value]) => (
            <div key={key} className="flex items-center gap-2 text-xs">
              <span className="w-24 capitalize text-gray-500">{key.replace("_", " ")}</span>
              <div className="flex-1 h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full">
                <div className={`h-full rounded-full ${value >= 80 ? "bg-green-500" : value >= 50 ? "bg-yellow-500" : "bg-red-500"}`}
                  style={{ width: `${value}%` }} />
              </div>
              <span className="w-8 text-right">{value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
