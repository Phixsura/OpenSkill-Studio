"use client";

interface CategoryCount { category: string; count: number; }
interface Props { averageRating: number; totalFeedback: number; categories: CategoryCount[]; lowRatedCount: number; appName: string; }

const catEmoji: Record<string, string> = { bug: "🐛", feature: "✨", docs: "📚", performance: "⚡", other: "💬" };
const stars = (r: number) => "★".repeat(Math.round(r)) + "☆".repeat(5 - Math.round(r));

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerFeedbackCollectorCard({ averageRating, totalFeedback, categories, lowRatedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💬 Consumer Feedback</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalFeedback} responses</p>
        </div>
        {lowRatedCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">⚠️ {lowRatedCount} low-rated</span>}
      </div>
      <div className="mb-3 text-center">
        <span className="text-lg font-bold text-yellow-500">{stars(averageRating)}</span>
        <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">{averageRating.toFixed(1)}</span>
      </div>
      {categories.length > 0 && (
        <div className="space-y-1">
          {categories.map((c) => (
            <div key={c.category} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{catEmoji[c.category] ?? "•"} {c.category}</span>
              <span className="text-gray-400">{c.count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
