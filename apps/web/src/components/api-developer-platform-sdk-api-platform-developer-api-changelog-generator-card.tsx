"use client";

interface ChangeInfo { change_id: string; change_type: string; description: string; breaking: boolean; }
interface Props { version: string; changes: ChangeInfo[]; breakingCount: number; appName: string; }

const typeEmoji: Record<string, string> = { added: "✨", changed: "🔄", deprecated: "⚠️", removed: "🗑️", fixed: "🐛", security: "🔒" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiChangelogGeneratorCard({ version, changes, breakingCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Changelog</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {version}</p>
        </div>
        {breakingCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">💥 {breakingCount} breaking</span>}
      </div>
      {changes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No changes</p>
      ) : (
        <div className="space-y-1">
          {changes.map((c) => (
            <div key={c.change_id} className="flex items-start gap-1.5 text-[11px]">
              <span>{typeEmoji[c.change_type] ?? "•"}</span>
              <span className="text-gray-700 dark:text-gray-300">{c.breaking && <span className="mr-1 font-semibold text-red-600 dark:text-red-400">BREAKING</span>}{c.description}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
