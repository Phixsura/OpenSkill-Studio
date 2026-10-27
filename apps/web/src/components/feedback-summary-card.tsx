"use client";

interface FeedbackEntry {
  feedback_id: string;
  user_id: string;
  rating: number;
  comment: string;
  sentiment: "positive" | "neutral" | "negative";
  created_at: string;
}

interface FeedbackSummaryData {
  app_id: string;
  total_count: number;
  avg_rating: number;
  distribution: Record<number, number>;
  sentiment_breakdown: Record<string, number>;
  recent: FeedbackEntry[];
}

interface FeedbackSummaryCardProps {
  summary: FeedbackSummaryData;
  appName: string;
}

const SENT_STYLES: Record<string, { label: string; color: string }> = {
  positive: { label: "Positive", color: "text-green-600" },
  neutral: { label: "Neutral", color: "text-gray-500" },
  negative: { label: "Negative", color: "text-red-600" },
};

function StarDisplay({ rating }: { rating: number }) {
  return (
    <span className="text-yellow-500" aria-label={`${rating} stars`}>
      {"★".repeat(rating)}
      {"☆".repeat(5 - rating)}
    </span>
  );
}

function DistributionBar({ star, count, max }: { star: number; count: number; max: number }) {
  const pct = max > 0 ? (count / max) * 100 : 0;
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="w-4 text-right text-gray-500">{star}</span>
      <span className="text-yellow-500">★</span>
      <div className="h-2 flex-1 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-full rounded-full bg-yellow-400" style={{ width: `${pct}%` }} />
      </div>
      <span className="w-6 text-right text-gray-400">{count}</span>
    </div>
  );
}

export function FeedbackSummaryCard({ summary, appName }: FeedbackSummaryCardProps) {
  const maxCount = Math.max(...Object.values(summary.distribution), 1);

  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div>
          <h3 className="font-semibold">User Feedback</h3>
          <p className="text-xs text-gray-500">
            {appName} • {summary.total_count} reviews
          </p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold">{summary.avg_rating}</p>
          <StarDisplay rating={Math.round(summary.avg_rating)} />
        </div>
      </div>

      {/* Distribution */}
      <div className="space-y-1 px-4 py-3">
        {[5, 4, 3, 2, 1].map((star) => (
          <DistributionBar
            key={star}
            star={star}
            count={summary.distribution[star] ?? 0}
            max={maxCount}
          />
        ))}
      </div>

      {/* Sentiment */}
      <div className="flex gap-3 border-t border-gray-200 px-4 py-2 text-xs dark:border-gray-700">
        {Object.entries(summary.sentiment_breakdown).map(([s, count]) => {
          const st = SENT_STYLES[s] ?? SENT_STYLES.neutral;
          return (
            <span key={s} className={st.color}>
              {count} {st.label}
            </span>
          );
        })}
      </div>

      {/* Recent */}
      {summary.recent.length > 0 && (
        <div className="border-t border-gray-200 dark:border-gray-700">
          <div className="px-4 py-2">
            <p className="text-[10px] font-semibold uppercase text-gray-400">Recent</p>
          </div>
          <div className="divide-y divide-gray-100 dark:divide-gray-800">
            {summary.recent.map((fb) => (
              <div key={fb.feedback_id} className="px-4 py-2">
                <div className="flex items-center gap-2">
                  <StarDisplay rating={fb.rating} />
                  <span className="text-xs text-gray-400">{fb.user_id}</span>
                </div>
                {fb.comment && (
                  <p className="mt-0.5 text-xs text-gray-600 dark:text-gray-400">{fb.comment}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {summary.total_count === 0 && (
        <div className="py-6 text-center text-sm text-gray-500">No feedback yet</div>
      )}
    </div>
  );
}
