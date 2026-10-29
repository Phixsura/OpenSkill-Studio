"use client";

interface CategoryCount { category: string; count: number; }
interface Props { categories: CategoryCount[]; totalErrors: number; appName: string; }

const catEmoji: Record<string, string> = { client: "🔸", server: "🔴", auth: "🔒", rate_limit: "⏱️", validation: "❌", timeout: "⌛", not_found: "🔍" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiErrorClassifierCard({ categories, totalErrors, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔍 Error Classifier</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-red-600 dark:text-red-400">{totalErrors.toLocaleString()}</span>
      </div>
      {categories.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No errors classified</p>
      ) : (
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
