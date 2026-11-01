"use client";

interface ScoreInfo { consumer_id: string; score: number; sentiment: string; }
interface Props { scores: ScoreInfo[]; averageScore: number; appName: string; }

const sentimentEmoji: Record<string, string> = { delighted: "😊", satisfied: "🙂", neutral: "😐", dissatisfied: "😟" };
const sentimentColor: Record<string, string> = { delighted: "text-green-600 dark:text-green-400", satisfied: "text-blue-600 dark:text-blue-400", neutral: "text-gray-400", dissatisfied: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerSatisfactionCard({ scores, averageScore, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">😊 Satisfaction</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-lg font-bold text-gray-900 dark:text-gray-100">{averageScore}</span>
      </div>
      {scores.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No satisfaction data</p>
      ) : (
        <div className="space-y-1">
          {scores.map((s) => (
            <div key={s.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{sentimentEmoji[s.sentiment]} {s.consumer_id}</span>
              <span className={sentimentColor[s.sentiment]}>{s.score} · {s.sentiment}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
