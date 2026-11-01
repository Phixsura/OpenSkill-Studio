"use client";

interface SectionScore {
  score: number;
  max: number;
}

interface ListingScore {
  total: number;
  maxScore: number;
  grade: string;
  sections: Record<string, SectionScore>;
  suggestions: string[];
}

const gradeColors: Record<string, string> = {
  A: "text-green-600 bg-green-100 dark:bg-green-900/30",
  B: "text-blue-600 bg-blue-100 dark:bg-blue-900/30",
  C: "text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30",
  D: "text-orange-600 bg-orange-100 dark:bg-orange-900/30",
  F: "text-red-600 bg-red-100 dark:bg-red-900/30",
};

const sectionLabels: Record<string, string> = {
  title: "📝 Title", description: "📄 Description", media: "🖼️ Media",
  metadata: "🏷️ Metadata", resources: "📚 Resources",
};

export function ListingScoreCard({ score }: { score: ListingScore }) {
  const pct = Math.round((score.total / score.maxScore) * 100);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📊 Listing Score</h2>
        <div className="flex items-center gap-2">
          <span className={`text-2xl font-bold w-10 h-10 rounded-full flex items-center justify-center ${gradeColors[score.grade]}`}>
            {score.grade}
          </span>
          <span className="text-sm text-gray-500">{score.total}/{score.maxScore} ({pct}%)</span>
        </div>
      </div>

      <div className="space-y-2">
        {Object.entries(score.sections).map(([key, section]) => {
          const barPct = Math.round((section.score / section.max) * 100);
          return (
            <div key={key}>
              <div className="flex justify-between text-sm mb-0.5">
                <span>{sectionLabels[key] || key}</span>
                <span className="text-gray-500">{section.score}/{section.max}</span>
              </div>
              <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${barPct >= 80 ? "bg-green-500" : barPct >= 50 ? "bg-yellow-500" : "bg-red-500"}`}
                  style={{ width: `${barPct}%` }} />
              </div>
            </div>
          );
        })}
      </div>

      {score.suggestions.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-1">💡 Suggestions</h3>
          <ul className="space-y-1">
            {score.suggestions.map((s, i) => (
              <li key={i} className="text-xs text-gray-600 dark:text-gray-400 flex gap-1">
                <span className="text-yellow-500">•</span> {s}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
