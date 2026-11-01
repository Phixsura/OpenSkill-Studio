"use client";

interface FeedbackItem { id: string; rating: number; category: string; comment: string; status: string; createdAt: string; }
interface Props { feedback: FeedbackItem[]; averageRating: number; totalCount: number; appName: string; }

const stars = (n: number) => "★".repeat(n) + "☆".repeat(5 - n);

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerFeedbackCard({ feedback, averageRating, totalCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⭐ Consumer Feedback</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {totalCount} responses</p>
        </div>
        <span className="text-lg font-bold text-amber-500">{averageRating}/5</span>
      </div>
      {feedback.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No feedback yet</p>
      ) : (
        <div className="space-y-2">
          {feedback.slice(0, 5).map((f) => (
            <div key={f.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-amber-500">{stars(f.rating)}</span>
                <span className="rounded bg-gray-200 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-700">{f.category}</span>
              </div>
              {f.comment && <div className="mt-0.5 text-[10px] text-gray-500">{f.comment}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
