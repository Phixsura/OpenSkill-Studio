"use client";

interface DiffSummary {
  added: number;
  removed: number;
  modified: number;
}

interface DiffInfo {
  diff_id: string;
  from_version: string;
  to_version: string;
  change_count: number;
  summary: DiffSummary;
}

interface APIChangelogDiffCardProps {
  diffs: DiffInfo[];
  appName: string;
}

export default function APIChangelogDiffCard({ diffs, appName }: APIChangelogDiffCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔀 Changelog Diffs</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{diffs.length} diffs</span>
      </div>

      {diffs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No version diffs</p>
      ) : (
        <div className="space-y-2">
          {diffs.map((d) => (
            <div key={d.diff_id} className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-800 dark:text-gray-200">{d.from_version} → {d.to_version}</span>
                <span className="text-[10px] text-gray-400">{d.change_count} changes</span>
              </div>
              <div className="mt-1 flex gap-3 text-[10px]">
                <span className="text-green-600">+{d.summary.added}</span>
                <span className="text-red-500">-{d.summary.removed}</span>
                <span className="text-yellow-600">~{d.summary.modified}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
