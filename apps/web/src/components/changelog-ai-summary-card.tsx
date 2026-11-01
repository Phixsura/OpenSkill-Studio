"use client";

interface AISummaryInfo {
  version: string;
  headline: string;
  bullet_points: string[];
  breaking_count: number;
  category_counts: Record<string, number>;
  total_changes: number;
}

interface ChangelogAISummaryCardProps {
  summary: AISummaryInfo;
  appName: string;
}

export default function ChangelogAISummaryCard({ summary, appName }: ChangelogAISummaryCardProps) {
  const categories = Object.entries(summary.category_counts).sort((a, b) => b[1] - a[1]);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Release Summary
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {summary.breaking_count > 0 && (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            {summary.breaking_count} breaking
          </span>
        )}
      </div>

      <p className="mb-3 text-sm font-medium text-gray-800 dark:text-gray-200">
        {summary.headline}
      </p>

      {/* Category chips */}
      <div className="mb-3 flex flex-wrap gap-1.5">
        {categories.map(([cat, count]) => (
          <span
            key={cat}
            className="rounded-full bg-gray-100 px-2 py-0.5 text-[11px] text-gray-600 dark:bg-gray-800 dark:text-gray-400"
          >
            {cat} ({count})
          </span>
        ))}
      </div>

      {/* Bullet points */}
      <ul className="space-y-1">
        {summary.bullet_points.map((b, i) => (
          <li
            key={i}
            className={`flex items-start gap-1.5 text-xs ${
              b.startsWith("⚠")
                ? "font-medium text-red-600 dark:text-red-400"
                : "text-gray-700 dark:text-gray-300"
            }`}
          >
            <span className="mt-0.5">{b.startsWith("⚠") ? "" : "•"}</span>
            <span>{b}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
