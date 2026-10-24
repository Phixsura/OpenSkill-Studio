"use client";

interface FeedbackSummaryCardProps { count: number; avgRating: number;
  nps: number; byRating: Record<string, number>; }

export function FeedbackSummaryCard({ count, avgRating, nps, byRating }: FeedbackSummaryCardProps) {
  const maxCount = Math.max(...Object.values(byRating), 1);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💬 User Feedback</h3>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold">{count}</div>
          <div className="text-[10px] text-gray-400">Responses</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold">⭐ {avgRating}</div>
          <div className="text-[10px] text-gray-400">Avg Rating</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className={`text-lg font-bold ${nps >= 0 ? "text-green-600" : "text-red-600"}`}>{nps > 0 ? "+" : ""}{nps}</div>
          <div className="text-[10px] text-gray-400">NPS</div>
        </div>
      </div>
      <div className="p-4 space-y-1.5">
        {[5, 4, 3, 2, 1].map(r => (
          <div key={r} className="flex items-center gap-2 text-xs">
            <span className="w-4 text-right">{r}★</span>
            <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className="h-full bg-yellow-500 rounded-full"
                style={{ width: `${((byRating[String(r)] ?? 0) / maxCount) * 100}%` }} />
            </div>
            <span className="text-gray-400 w-6 text-right">{byRating[String(r)] ?? 0}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
