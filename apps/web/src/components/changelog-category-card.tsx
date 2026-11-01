"use client";

interface CategoryCount {
  category: string;
  emoji: string;
  count: number;
}

interface ChangelogCategoryCardProps {
  categories: CategoryCount[];
  appName: string;
}

export default function ChangelogCategoryCard({ categories, appName }: ChangelogCategoryCardProps) {
  const totalEntries = categories.reduce((s, c) => s + c.count, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            📂 Changelog Categories
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{totalEntries} entries</span>
      </div>

      {categories.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No categories</p>
      ) : (
        <div className="space-y-1.5">
          {categories.map((c) => (
            <div
              key={c.category}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center gap-2">
                {c.emoji && <span>{c.emoji}</span>}
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                  {c.category}
                </span>
              </div>
              <span className="text-sm font-bold text-gray-900 dark:text-gray-100">{c.count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
