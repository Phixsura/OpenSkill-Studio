"use client";

interface ScoreDimension {
  name: string;
  value: number;
  weight: number;
  description: string;
}

export function DeveloperScoreCard({
  developerName,
  overallScore,
  grade,
  dimensions,
  tips,
}: {
  developerName: string;
  overallScore: number;
  grade: string;
  dimensions: ScoreDimension[];
  tips: { dimension: string; tip: string; current: number }[];
}) {
  const gradeColors: Record<string, string> = {
    "A+": "text-green-500", A: "text-green-500", B: "text-blue-500",
    C: "text-yellow-500", D: "text-orange-500", F: "text-red-500",
  };

  const barColor = (val: number) =>
    val >= 80 ? "bg-green-500" : val >= 60 ? "bg-yellow-500" : "bg-red-500";

  return (
    <div className="rounded-xl border dark:border-gray-700 p-5 space-y-5 max-w-md">
      {/* Header */}
      <div className="text-center">
        <h2 className="font-bold text-sm text-gray-500">{developerName}</h2>
        <div className={`text-5xl font-black ${gradeColors[grade] || "text-gray-500"}`}>{grade}</div>
        <div className="text-2xl font-bold">{overallScore}<span className="text-sm text-gray-400">/100</span></div>
        <div className="text-xs text-gray-400">Developer Score</div>
      </div>

      {/* Dimensions */}
      <div className="space-y-2">
        {dimensions.map((dim) => (
          <div key={dim.name}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className="capitalize">{dim.name.replace("_", " ")}</span>
              <span className="font-mono">{dim.value}/100</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div className={`h-2 rounded-full ${barColor(dim.value)}`}
                style={{ width: `${dim.value}%` }} />
            </div>
          </div>
        ))}
      </div>

      {/* Tips */}
      {tips.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold text-gray-500 mb-2">💡 Improvement Tips</h3>
          <div className="space-y-1">
            {tips.slice(0, 3).map((tip, i) => (
              <div key={i} className="text-xs bg-yellow-50 dark:bg-yellow-900/10 rounded-lg p-2 text-yellow-700 dark:text-yellow-300">
                {tip.tip}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
