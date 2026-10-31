"use client";

interface WordFreq { word: string; count: number; }
interface ReviewInsightsPanelProps { totalReviews: number; sentimentScore: number;
  sentiment: { positive: number; negative: number; neutral: number };
  commonWords: WordFreq[]; topics: Record<string, number>; avgRating: number; }

export function ReviewInsightsPanel({ totalReviews, sentimentScore, sentiment,
  commonWords, topics, avgRating }: ReviewInsightsPanelProps) {
  const sentimentEmoji = sentimentScore > 20 ? "😊" : sentimentScore < -20 ? "😞" : "😐";
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Review Insights</h2>
      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="rounded-lg bg-green-50 p-3 dark:bg-green-900/10">
          <p className="text-xl font-bold text-green-600">{sentiment.positive}</p>
          <p className="text-xs text-gray-400">Positive</p>
        </div>
        <div className="rounded-lg bg-gray-50 p-3 dark:bg-gray-800">
          <p className="text-xl font-bold">{sentiment.neutral}</p>
          <p className="text-xs text-gray-400">Neutral</p>
        </div>
        <div className="rounded-lg bg-red-50 p-3 dark:bg-red-900/10">
          <p className="text-xl font-bold text-red-600">{sentiment.negative}</p>
          <p className="text-xs text-gray-400">Negative</p>
        </div>
      </div>
      <div className="text-center">
        <span className="text-3xl">{sentimentEmoji}</span>
        <p className="text-sm">Sentiment: <strong>{sentimentScore > 0 ? "+" : ""}{sentimentScore}%</strong></p>
        <p className="text-xs text-gray-400">{totalReviews} reviews · ⭐ {avgRating} avg</p>
      </div>
      {commonWords.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-500">Common Words</h3>
          <div className="mt-1 flex flex-wrap gap-1">
            {commonWords.map(w => (
              <span key={w.word} className="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/20">
                {w.word} ({w.count})
              </span>
            ))}
          </div>
        </div>
      )}
      {Object.keys(topics).length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-500">Topics</h3>
          <div className="mt-1 flex flex-wrap gap-1">
            {Object.entries(topics).map(([topic, count]) => (
              <span key={topic} className="rounded-full border px-2.5 py-0.5 text-xs dark:border-gray-600">
                {topic} ({count})
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
