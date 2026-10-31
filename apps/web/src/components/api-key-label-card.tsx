"use client";

interface LabeledKeyInfo {
  key_id: string;
  name: string;
  labels: string[];
}

interface APIKeyLabelCardProps {
  keys: LabeledKeyInfo[];
  allLabels: string[];
  appName: string;
}

export default function APIKeyLabelCard({ keys, allLabels, appName }: APIKeyLabelCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏷️ Key Labels</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{keys.length} keys · {allLabels.length} labels</span>
      </div>

      {keys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No labeled keys</p>
      ) : (
        <div className="space-y-1.5">
          {keys.map((k) => (
            <div key={k.key_id} className="rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <span className="text-xs font-medium text-gray-800 dark:text-gray-200">{k.name}</span>
              <div className="mt-0.5 flex flex-wrap gap-1">
                {k.labels.map((l) => (
                  <span key={l} className="rounded-full bg-gray-100 px-1.5 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{l}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
