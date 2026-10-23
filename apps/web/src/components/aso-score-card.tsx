"use client";

interface AsoScoreCardProps { score: number; grade: string; suggestions: string[]; }

export function AsoScoreCard({ score, grade, suggestions }: AsoScoreCardProps) {
  const gradeColors: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-red-600" };
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Listing Quality</h3>
        <div className="text-right">
          <span className={`text-2xl font-bold ${gradeColors[grade] || ""}`}>{grade}</span>
          <p className="text-xs text-gray-400">{score}/100</p>
        </div>
      </div>
      {suggestions.length > 0 ? (
        <ul className="mt-3 space-y-1">
          {suggestions.map((s, i) => <li key={i} className="text-xs text-gray-600 dark:text-gray-400">💡 {s}</li>)}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-green-600">✅ Perfect listing!</p>
      )}
    </div>
  );
}
