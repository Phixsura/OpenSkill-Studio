"use client";

interface Note { id: string; version: string; title: string; type: string; publishedAt: string; }
interface Props { notes: Note[]; appName: string; }

const typeIcons: Record<string, string> = { feature: "✨", fix: "🐛", improvement: "⚡", breaking: "⚠️", security: "🔒" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiReleaseNoteCard({ notes, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📝 Release Notes</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {notes.length} published</p>
      </div>
      {notes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No release notes</p>
      ) : (
        <div className="space-y-1">
          {notes.slice(0, 8).map((n) => (
            <div key={n.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[11px] dark:bg-gray-800">
              <div className="flex items-center gap-1">
                <span>{typeIcons[n.type] ?? "📋"}</span>
                <span className="text-gray-700 dark:text-gray-300">{n.title}</span>
              </div>
              <span className="text-[10px] text-gray-400">v{n.version}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
