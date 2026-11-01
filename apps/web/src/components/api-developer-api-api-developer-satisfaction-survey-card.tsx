"use client";

interface Props { nps: number; avgSatisfaction: number; responseCount: number; recentComments: string[]; appName: string; }

const npsColor = (n: number) => n >= 50 ? "text-green-600" : n >= 0 ? "text-yellow-600" : "text-red-500";
const stars = (r: number) => "★".repeat(Math.round(r)) + "☆".repeat(5 - Math.round(r));

export default function APIDeveloperAPIApiDeveloperSatisfactionSurveyCard({ nps, avgSatisfaction, responseCount, recentComments, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">😊 Developer Satisfaction</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {responseCount} responses</p>
        </div>
        <div className="text-right">
          <span className={`text-lg font-bold ${npsColor(nps)}`}>{nps}</span>
          <p className="text-[9px] text-gray-400">NPS</p>
        </div>
      </div>
      <div className="mb-3 text-center">
        <span className="text-yellow-500">{stars(avgSatisfaction)}</span>
        <p className="text-[10px] text-gray-400">{avgSatisfaction}/5 avg satisfaction</p>
      </div>
      {recentComments.length > 0 && (
        <div className="space-y-1">
          {recentComments.slice(0, 3).map((c, i) => (
            <p key={i} className="truncate text-[10px] text-gray-500 dark:text-gray-400">"{c}"</p>
          ))}
        </div>
      )}
    </div>
  );
}
