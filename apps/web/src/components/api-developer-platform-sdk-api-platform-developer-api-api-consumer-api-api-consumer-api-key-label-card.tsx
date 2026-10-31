"use client";

interface LabelInfo { key_id: string; label: string; environment: string; tags: string[]; }
interface Props { labels: LabelInfo[]; appName: string; }

const envColor: Record<string, string> = { production: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400", staging: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400", development: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400", test: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiKeyLabelCard({ labels, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏷️ API Key Labels</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {labels.length} keys</p>
      </div>
      {labels.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No labeled keys</p>
      ) : (
        <div className="space-y-1.5">
          {labels.map((l) => (
            <div key={l.key_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{l.label}</span>
                <span className={`rounded px-1 text-[9px] font-medium ${envColor[l.environment] ?? ""}`}>{l.environment}</span>
              </div>
              {l.tags.length > 0 && <div className="flex gap-1 mt-0.5">{l.tags.map((t) => <span key={t} className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">{t}</span>)}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
