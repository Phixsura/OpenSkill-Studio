"use client";

interface FeedbackInfo { feedback_id: string; page_path: string; helpful: boolean; comment: string; }
interface Props { totalFeedback: number; helpfulnessRate: number; worstPages: [string, number][]; recentComments: FeedbackInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiDeveloperApiDocumentationFeedbackCard({ totalFeedback, helpfulnessRate, worstPages, recentComments, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📝 Doc Feedback</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalFeedback} responses</p>
        </div>
        <span className={`text-sm font-bold ${helpfulnessRate >= 80 ? "text-green-600" : helpfulnessRate >= 50 ? "text-yellow-600" : "text-red-500"}`}>{helpfulnessRate}% helpful</span>
      </div>
      {worstPages.length > 0 && (
        <div className="mb-3">
          <p className="text-[10px] font-medium text-gray-500 mb-1">Needs improvement:</p>
          {worstPages.map(([page, rate]) => (
            <div key={page} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{page}</span>
              <span className="text-red-500">{rate}%</span>
            </div>
          ))}
        </div>
      )}
      {recentComments.length > 0 && (
        <div className="space-y-1">
          {recentComments.slice(0, 3).map((f) => (
            <p key={f.feedback_id} className="text-[10px] text-gray-500 truncate">{f.helpful ? "👍" : "👎"} {f.comment}</p>
          ))}
        </div>
      )}
    </div>
  );
}
