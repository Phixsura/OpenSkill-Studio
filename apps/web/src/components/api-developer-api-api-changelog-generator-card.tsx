"use client";

interface EntryInfo { entry_id: string; category: string; description: string; breaking: boolean; }
interface ChangelogInfo { version: string; entries: EntryInfo[]; published: boolean; breaking_count: number; }
interface Props { changelogs: ChangelogInfo[]; appName: string; }

const catIcon: Record<string, string> = { added: "✨", changed: "🔄", deprecated: "⚠️", removed: "🗑️", fixed: "🐛", security: "🔒" };

export default function APIDeveloperAPIApiChangelogGeneratorCard({ changelogs, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📝 Changelog Generator</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {changelogs.length} versions</p>
      </div>
      {changelogs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No changelogs</p>
      ) : (
        <div className="space-y-3">
          {changelogs.map((c) => (
            <div key={c.version} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-1.5">
                  <span className="font-bold text-gray-900 dark:text-gray-100">{c.version}</span>
                  {c.published && <span className="rounded bg-green-100 px-1 py-0.5 text-[9px] text-green-700">published</span>}
                </div>
                <span className="text-gray-400">{c.entries.length} changes{c.breaking_count > 0 ? ` · ${c.breaking_count} breaking` : ""}</span>
              </div>
              <div className="mt-1 space-y-0.5">
                {c.entries.slice(0, 3).map((e) => (
                  <p key={e.entry_id} className="text-[10px] text-gray-500">{catIcon[e.category] ?? "•"} {e.description}</p>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
