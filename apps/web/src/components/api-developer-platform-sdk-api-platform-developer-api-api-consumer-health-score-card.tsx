"use client";

interface ScoreInfo { consumer_id: string; score: number; grade: string; risk_level: string; }
interface Props { scores: ScoreInfo[]; atRiskCount: number; appName: string; }

const gradeColor: Record<string, string> = { A: "text-green-600 dark:text-green-400", B: "text-blue-600 dark:text-blue-400", C: "text-yellow-600 dark:text-yellow-400", D: "text-orange-600 dark:text-orange-400", F: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerHealthScoreCard({ scores, atRiskCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💊 Health Scores</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {scores.length} consumers</p>
        </div>
        {atRiskCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">⚠️ {atRiskCount} at risk</span>}
      </div>
      {scores.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No health data</p>
      ) : (
        <div className="space-y-1">
          {scores.map((s) => (
            <div key={s.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.consumer_id}</span>
              <div className="flex items-center gap-2">
                <span className="text-gray-400">{s.score}</span>
                <span className={`font-bold ${gradeColor[s.grade] ?? ""}`}>{s.grade}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
