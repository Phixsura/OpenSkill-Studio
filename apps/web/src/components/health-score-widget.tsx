"use client";

interface HealthScoreWidgetProps { score: number; grade: string;
  breakdown: Record<string, number>; }

const GRADE_STYLE: Record<string, string> = {
  A: "text-green-600", B: "text-blue-500", C: "text-yellow-600", D: "text-orange-500", F: "text-red-600",
};

export function HealthScoreWidget({ score, grade, breakdown }: HealthScoreWidgetProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💯 Health Score</h3>
        <div className="flex items-center gap-2">
          <span className="text-2xl font-black">{score}</span>
          <span className={`text-xl font-black ${GRADE_STYLE[grade] ?? ""}`}>{grade}</span>
        </div>
      </div>
      <div className="p-4 space-y-2">
        {Object.entries(breakdown).map(([key, val]) => (
          <div key={key}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className="text-gray-500 capitalize">{key.replace("_", " ")}</span>
              <span className="text-gray-400">{val}</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${val >= 80 ? "bg-green-500" : val >= 50 ? "bg-yellow-500" : "bg-red-500"}`}
                style={{ width: `${Math.min(val, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
