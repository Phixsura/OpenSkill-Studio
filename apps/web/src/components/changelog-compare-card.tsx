"use client";

interface CompareEntryInfo {
  title: string;
  category: string;
  breaking: boolean;
}

interface ChangelogCompareCardProps {
  fromVersion: string;
  toVersion: string;
  entries: CompareEntryInfo[];
  categoryCounts: Record<string, number>;
  breakingCount: number;
  appName: string;
}

const CAT_COLORS: Record<string, string> = {
  added: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  fixed: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  changed: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  removed: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export default function ChangelogCompareCard({
  fromVersion,
  toVersion,
  entries,
  categoryCounts,
  breakingCount,
  appName,
}: ChangelogCompareCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Version Compare
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="font-mono text-xs text-gray-500">
          v{fromVersion} → v{toVersion}
        </span>
      </div>

      <div className="mb-3 flex items-center gap-2">
        <span className="text-xs text-gray-400">{entries.length} changes</span>
        {breakingCount > 0 && (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            {breakingCount} breaking
          </span>
        )}
        {Object.entries(categoryCounts).map(([cat, count]) => (
          <span
            key={cat}
            className={`rounded px-1.5 py-0.5 text-[10px] ${CAT_COLORS[cat] ?? "bg-gray-100 text-gray-600"}`}
          >
            {cat} {count}
          </span>
        ))}
      </div>

      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No changes in this range</p>
      ) : (
        <ul className="space-y-1">
          {entries.slice(0, 10).map((e, i) => (
            <li key={i} className="flex items-start gap-1.5 text-xs">
              <span className="mt-0.5 text-gray-400">•</span>
              <span
                className={
                  e.breaking
                    ? "font-medium text-red-600 dark:text-red-400"
                    : "text-gray-700 dark:text-gray-300"
                }
              >
                {e.breaking && "⚠ "}
                {e.title}
              </span>
            </li>
          ))}
          {entries.length > 10 && (
            <li className="text-center text-[11px] text-gray-400">+{entries.length - 10} more</li>
          )}
        </ul>
      )}
    </div>
  );
}
