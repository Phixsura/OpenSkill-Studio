"use client";

interface AppScoreCardProps { score: number; grade: string; criteria: Record<string, number>;
  improvements: string[]; }

const gradeColor: Record<string, string> = {
  "A+": "text-green-600", A: "text-green-600", B: "text-blue-600",
  C: "text-yellow-600", D: "text-orange-600", F: "text-red-600",
};

const criteriaLabels: Record<string, string> = {
  description_quality: "Description", screenshots: "Screenshots", documentation: "Docs",
  testing: "Tests", rating: "Rating", installs: "Installs",
  update_frequency: "Updates", support: "Support",
};

export function AppScoreCard({ score, grade, criteria, improvements }: AppScoreCardProps) {
  return (
    <div className="space-y-4 rounded-lg border p-5 dark:border-gray-700">
      <div className="text-center">
        <span className={`text-5xl font-black ${gradeColor[grade] ?? ""}`}>{grade}</span>
        <p className="mt-1 text-lg font-bold">{score}/100</p>
        <p className="text-xs text-gray-400">App Quality Score</p>
      </div>
      <div className="space-y-1.5">
        {Object.entries(criteria).map(([key, val]) => (
          <div key={key}>
            <div className="flex justify-between text-xs">
              <span>{criteriaLabels[key] ?? key}</span>
              <span className="text-gray-400">{val}/20</span>
            </div>
            <div className="mt-0.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
              <div className="h-full rounded-full bg-blue-500" style={{ width: `${(val / 20) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
      {improvements.length > 0 && (
        <div>
          <p className="text-xs font-medium text-gray-500">💡 Improve:</p>
          <p className="text-xs text-gray-400">{improvements.map(i => criteriaLabels[i] ?? i).join(", ")}</p>
        </div>
      )}
    </div>
  );
}
