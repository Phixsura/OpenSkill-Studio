"use client";

interface FeedbackFormCardProps {
  avgRating: number;
  nps: number;
  totalCount: number;
  categories: Record<string, number>;
  appName: string;
}

export default function APIFeedbackFormCard({ avgRating, nps, totalCount, categories, appName }: FeedbackFormCardProps) {
  const catList = Object.entries(categories).sort((a, b) => b[1] - a[1]);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💬 Developer Feedback</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{totalCount} responses</span>
      </div>

      <div className="mb-3 grid grid-cols-2 gap-2 text-center">
        <div className="rounded-lg bg-gray-50 py-1.5 dark:bg-gray-800">
          <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{avgRating}</p>
          <p className="text-[9px] text-gray-500">avg rating</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-1.5 dark:bg-gray-800">
          <p className={`text-lg font-bold ${nps >= 50 ? "text-green-600" : nps >= 0 ? "text-yellow-600" : "text-red-500"}`}>{nps}</p>
          <p className="text-[9px] text-gray-500">NPS</p>
        </div>
      </div>

      {catList.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {catList.map(([cat, count]) => (
            <span key={cat} className="rounded bg-gray-100 px-1.5 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{cat}: {count}</span>
          ))}
        </div>
      )}
    </div>
  );
}
