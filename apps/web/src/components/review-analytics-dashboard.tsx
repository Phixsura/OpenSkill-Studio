"use client";

interface Sentiment { positive: number; neutral: number; negative: number; nps: number; }
interface Keyword { word: string; count: number; }
interface ReviewAnalyticsDashboardProps { total: number; avgRating: number; sentiment: Sentiment;
  keywords: Keyword[]; replyRate: number; }

export function ReviewAnalyticsDashboard({ total, avgRating, sentiment, keywords, replyRate }: ReviewAnalyticsDashboardProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Review Analytics</h2>
      <div className="grid grid-cols-4 gap-3">
        <div className="rounded-lg border border-gray-200 p-3 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{total}</p><p className="text-xs text-gray-400">Total</p>
        </div>
        <div className="rounded-lg border border-gray-200 p-3 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{avgRating} ★</p><p className="text-xs text-gray-400">Average</p>
        </div>
        <div className="rounded-lg border border-gray-200 p-3 text-center dark:border-gray-700">
          <p className={`text-2xl font-bold ${sentiment.nps >= 0 ? "text-green-600" : "text-red-600"}`}>{sentiment.nps}</p>
          <p className="text-xs text-gray-400">NPS</p>
        </div>
        <div className="rounded-lg border border-gray-200 p-3 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{replyRate}%</p><p className="text-xs text-gray-400">Reply Rate</p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
          <h3 className="text-sm font-semibold">Sentiment</h3>
          <div className="mt-2 space-y-1">
            <div className="flex justify-between text-sm"><span className="text-green-600">Positive</span><span>{sentiment.positive}</span></div>
            <div className="flex justify-between text-sm"><span className="text-gray-500">Neutral</span><span>{sentiment.neutral}</span></div>
            <div className="flex justify-between text-sm"><span className="text-red-600">Negative</span><span>{sentiment.negative}</span></div>
          </div>
        </div>
        <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
          <h3 className="text-sm font-semibold">Top Keywords</h3>
          <div className="mt-2 flex flex-wrap gap-1">
            {keywords.slice(0, 10).map(k => (
              <span key={k.word} className="rounded bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-700">{k.word} ({k.count})</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
