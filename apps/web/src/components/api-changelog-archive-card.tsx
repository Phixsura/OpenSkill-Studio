"use client";

interface ArchiveInfo { entry_id: string; title: string; version: string; archived: boolean; }
interface Props { entries: ArchiveInfo[]; appName: string; }

export default function APIChangelogArchiveCard({ entries, appName }: Props) {
  const active = entries.filter((e) => !e.archived).length;
  const archived = entries.filter((e) => e.archived).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📦 Changelog Archive</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{active} active · {archived} archived</span>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No entries</p>
      ) : (
        <div className="space-y-1">
          {entries.map((e) => (
            <div key={e.entry_id} className={`flex items-center justify-between text-[11px] ${e.archived ? "opacity-50" : ""}`}>
              <span className="text-gray-700 dark:text-gray-300">{e.title}</span>
              <div className="flex items-center gap-1.5">
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{e.version}</span>
                {e.archived && <span className="text-[9px] text-gray-400">archived</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
