"use client";

interface LabelInfo {
  label_id: string;
  name: string;
  color: string;
}

interface APIChangelogLabelCardProps {
  labels: LabelInfo[];
  appName: string;
}

export default function APIChangelogLabelCard({ labels, appName }: APIChangelogLabelCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏷️ Changelog Labels</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{labels.length} labels</span>
      </div>

      {labels.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No labels</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {labels.map((l) => (
            <span key={l.label_id} className="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs text-gray-700 dark:text-gray-300" style={{ backgroundColor: `${l.color}20` }}>
              <span className="h-2 w-2 rounded-full" style={{ backgroundColor: l.color }} />
              {l.name}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
