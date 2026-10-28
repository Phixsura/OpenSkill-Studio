"use client";

interface ReleaseNoteInfo {
  note_id: string;
  version: string;
  title: string;
  highlights: string[];
  known_issues: string[];
  published: boolean;
}

interface APIReleaseNoteCardProps {
  notes: ReleaseNoteInfo[];
  appName: string;
}

export default function APIReleaseNoteCard({ notes, appName }: APIReleaseNoteCardProps) {
  const published = notes.filter((n) => n.published).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📣 Release Notes</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{published}/{notes.length} published</span>
      </div>

      {notes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No release notes</p>
      ) : (
        <div className="space-y-2">
          {notes.map((n) => (
            <div key={n.note_id} className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-gray-800 dark:text-gray-200">{n.title}</span>
                  <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{n.version}</span>
                </div>
                {n.published && <span className="text-[9px] text-green-600">published</span>}
              </div>
              <div className="mt-1 text-[10px] text-gray-400">
                {n.highlights.length} highlights{n.known_issues.length > 0 ? ` · ${n.known_issues.length} known issues` : ""}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
