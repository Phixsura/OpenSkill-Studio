"use client";

interface ErrorSummary {
  total: number;
  by_type: Record<string, number>;
  unique_types: number;
}

interface ErrorSummaryCardProps {
  summary: ErrorSummary;
  appName?: string;
}

export function ErrorSummaryCard({ summary, appName }: ErrorSummaryCardProps) {
  const sorted = Object.entries(summary.by_type).sort((a, b) => b[1] - a[1]);

  if (summary.total === 0) {
    return (
      <div className="rounded-lg border border-green-200 bg-green-50 p-4 dark:border-green-800 dark:bg-green-900/20">
        <p className="text-sm text-green-700 dark:text-green-300">✅ No errors{appName ? ` for ${appName}` : ""}</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-900/20">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="font-semibold text-red-800 dark:text-red-200">
          {summary.total} Error{summary.total !== 1 ? "s" : ""}
        </h4>
        <span className="text-xs text-red-600 dark:text-red-400">{summary.unique_types} type{summary.unique_types !== 1 ? "s" : ""}</span>
      </div>
      <ul className="space-y-1">
        {sorted.slice(0, 5).map(([type, count]) => (
          <li key={type} className="flex items-center justify-between text-sm">
            <span className="font-mono text-xs text-red-700 dark:text-red-300">{type}</span>
            <span className="rounded bg-red-100 px-1.5 py-0.5 text-xs dark:bg-red-900">{count}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
