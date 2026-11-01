"use client";

interface NoteInfo { version: string; title: string; summary: string; highlights: string[]; breaking_changes: string[]; published: boolean; }
interface Props { notes: NoteInfo[]; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiPlatformReleaseNotesCard({ notes, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Release Notes</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {notes.length} releases</p>
      </div>
      {notes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No release notes</p>
      ) : (
        <div className="space-y-3">
          {notes.map((n) => (
            <div key={n.version} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-1.5">
                  <span className="font-bold text-gray-900 dark:text-gray-100">{n.version}</span>
                  <span className="text-gray-500">{n.title}</span>
                </div>
                {n.published && <span className="rounded bg-green-100 px-1 py-0.5 text-[9px] text-green-700">published</span>}
              </div>
              {n.highlights.length > 0 && (
                <div className="mt-1 space-y-0.5">
                  {n.highlights.slice(0, 3).map((h, i) => <p key={i} className="text-[10px] text-gray-500">✨ {h}</p>)}
                </div>
              )}
              {n.breaking_changes.length > 0 && <p className="mt-0.5 text-[10px] text-red-500">⚠️ {n.breaking_changes.length} breaking changes</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
