"use client";

interface CategoryStat { count: number; avgRating: number; }
interface FeedbackSummaryCardProps { total: number; avgRating: number; nps: number;
  byCategory: Record<string, CategoryStat>; promoters: number; detractors: number; }

export function FeedbackSummaryCard({ total, avgRating, nps, byCategory, promoters, detractors }: FeedbackSummaryCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">💬 User Feedback</h3>
      <div className="grid grid-cols-3 gap-3 text-center mb-4">
        <div><p className="text-2xl font-bold">{avgRating}</p><p className="text-xs text-gray-400">Avg Rating</p></div>
        <div><p className={`text-2xl font-bold ${nps >= 0 ? "text-green-600" : "text-red-600"}`}>{nps}</p><p className="text-xs text-gray-400">NPS</p></div>
        <div><p className="text-2xl font-bold">{total}</p><p className="text-xs text-gray-400">Responses</p></div>
      </div>
      <div className="flex gap-4 text-xs text-gray-400 mb-3">
        <span className="text-green-600">👍 {promoters} promoters</span>
        <span className="text-red-500">👎 {detractors} detractors</span>
      </div>
      <div className="space-y-1">
        {Object.entries(byCategory).map(([cat, stat]) => (
          <div key={cat} className="flex justify-between text-sm bg-gray-50 dark:bg-gray-800 rounded px-3 py-1.5">
            <span className="capitalize">{cat}</span>
            <span className="text-gray-400">{stat.count} · ⭐ {stat.avgRating}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
