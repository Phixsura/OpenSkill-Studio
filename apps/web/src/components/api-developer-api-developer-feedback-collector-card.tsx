"use client";

interface FeedbackInfo { feedback_id: string; developer_id: string; category: string; rating: number; comment: string; status: string; }
interface Props { feedback: FeedbackInfo[]; avgRating: number; categoryBreakdown: Record<string, number>; appName: string; }

const stars = (r: number) => "★".repeat(r) + "☆".repeat(5 - r);

export default function APIDeveloperAPIDeveloperFeedbackCollectorCard({ feedback, avgRating, categoryBreakdown, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💬 Developer Feedback</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {feedback.length} submissions</p>
        </div>
        <div className="text-right">
          <span className="text-sm font-bold text-yellow-500">{avgRating}</span>
          <p className="text-[9px] text-yellow-400">{stars(Math.round(avgRating))}</p>
        </div>
      </div>
      <div className="mb-3 flex flex-wrap gap-1.5">
        {Object.entries(categoryBreakdown).map(([cat, count]) => (
          <span key={cat} className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600 dark:bg-gray-800 dark:text-gray-300">{cat}: {count}</span>
        ))}
      </div>
      {feedback.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No feedback yet</p>
      ) : (
        <div className="space-y-1.5">
          {feedback.slice(0, 5).map((f) => (
            <div key={f.feedback_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-yellow-500">{stars(f.rating)}</span>
                <span className="text-gray-400">{f.category}</span>
              </div>
              <p className="truncate text-gray-600 dark:text-gray-400">{f.comment}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
