"use client";

interface SeoIssue { field: string; issue: string; impact: number; }
interface SeoScoreCardProps { score: number; grade: string; issues: SeoIssue[];
  onFix: (field: string) => void; }

const gradeColor: Record<string, string> = {
  A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", F: "text-red-600",
};

export function SeoScoreCard({ score, grade, issues, onFix }: SeoScoreCardProps) {
  return (
    <div className="space-y-4 rounded-lg border p-5 dark:border-gray-700">
      <div className="text-center">
        <span className={`text-4xl font-black ${gradeColor[grade] ?? ""}`}>{grade}</span>
        <p className="text-lg font-bold">{score}/100</p>
        <p className="text-xs text-gray-400">SEO Score</p>
      </div>
      {issues.length > 0 ? (
        <div className="space-y-1.5">
          {issues.map((iss, i) => (
            <div key={i} className="flex items-center justify-between rounded border border-yellow-200 px-3 py-2 dark:border-yellow-800">
              <div>
                <p className="text-sm">{iss.issue}</p>
                <p className="text-xs text-gray-400">{iss.field} · {iss.impact} points</p>
              </div>
              <button onClick={() => onFix(iss.field)} className="text-xs text-blue-500">Fix</button>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-center text-sm text-green-600">✅ No SEO issues found</p>
      )}
    </div>
  );
}
