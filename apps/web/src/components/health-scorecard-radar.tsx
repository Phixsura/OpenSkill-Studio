"use client";

interface HealthScorecardRadarProps {
  compositeScore: number; grade: string;
  dimensions: Record<string, number>; weakestDimension: string;
  recommendations: string[];
}

const DIM_LABELS: Record<string, string> = {
  availability: "Availability", performance: "Performance", security: "Security",
  compliance: "Compliance", dx: "Developer Experience",
};

export function HealthScorecardRadar({ compositeScore, grade, dimensions, weakestDimension, recommendations }: HealthScorecardRadarProps) {
  const gradeColors: Record<string, string> = { "A+": "text-green-600", A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-orange-600", F: "text-red-600" };

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Health Scorecard</h3>
        <div className="text-right">
          <span className={`text-3xl font-bold ${gradeColors[grade] || ""}`}>{grade}</span>
          <p className="text-xs text-gray-400">{compositeScore}/100</p>
        </div>
      </div>
      <div className="mt-4 space-y-2">
        {Object.entries(dimensions).map(([key, value]) => (
          <div key={key}>
            <div className="flex justify-between text-xs">
              <span className={key === weakestDimension ? "font-bold text-red-600" : ""}>{DIM_LABELS[key] || key}</span>
              <span>{value}</span>
            </div>
            <div className="mt-0.5 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
              <div className={`h-full rounded-full ${value >= 80 ? "bg-green-500" : value >= 60 ? "bg-yellow-500" : "bg-red-500"}`}
                style={{ width: `${value}%` }} />
            </div>
          </div>
        ))}
      </div>
      {recommendations.length > 0 && (
        <div className="mt-4">
          <p className="text-xs font-medium text-gray-500">Recommendations</p>
          <ul className="mt-1 space-y-0.5">
            {recommendations.map((r, i) => <li key={i} className="text-xs text-gray-600 dark:text-gray-400">💡 {r}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
