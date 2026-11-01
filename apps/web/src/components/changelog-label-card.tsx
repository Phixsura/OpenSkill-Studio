"use client";

interface LabelInfo {
  label_id: string;
  name: string;
  category: string;
  color: string;
  count: number;
}

interface ChangelogLabelCardProps {
  labels: LabelInfo[];
  appName: string;
  totalEntries: number;
}

export default function ChangelogLabelCard({
  labels,
  appName,
  totalEntries,
}: ChangelogLabelCardProps) {
  const categories = [...new Set(labels.map((l) => l.category))].sort();

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Changelog Labels
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {labels.length} labels · {totalEntries} entries
        </span>
      </div>

      {labels.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No labels defined</p>
      ) : (
        <div className="space-y-3">
          {categories.map((cat) => (
            <div key={cat}>
              <p className="mb-1 text-[10px] font-medium uppercase tracking-wider text-gray-500">
                {cat}
              </p>
              <div className="flex flex-wrap gap-1.5">
                {labels
                  .filter((l) => l.category === cat)
                  .map((l) => (
                    <span
                      key={l.label_id}
                      className="inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[11px] font-medium"
                      style={{ backgroundColor: `${l.color}20`, color: l.color }}
                    >
                      <span className="h-2 w-2 rounded-full" style={{ backgroundColor: l.color }} />
                      {l.name}
                      <span className="ml-0.5 opacity-70">{l.count}</span>
                    </span>
                  ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
