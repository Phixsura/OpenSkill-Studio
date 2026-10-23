"use client";

interface Change { type: string; description: string; }
interface ChangelogEntry { version: string; released_at?: string; changes: Change[]; has_breaking?: boolean; }
interface ChangelogPageViewerProps { entries: ChangelogEntry[]; page: number; totalPages: number; onPageChange: (p: number) => void; }

const TYPE_ICONS: Record<string, string> = { feat: "✨", fix: "🐛", perf: "⚡", breaking: "⚠️", docs: "📝" };

export function ChangelogPageViewer({ entries, page, totalPages, onPageChange }: ChangelogPageViewerProps) {
  return (
    <div className="space-y-4">
      {entries.map(e => (
        <div key={e.version} className={`rounded-lg border p-4 ${e.has_breaking ? "border-yellow-300 dark:border-yellow-700" : "border-gray-200 dark:border-gray-700"}`}>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold">{e.version}</h3>
            {e.released_at && <span className="text-xs text-gray-400">{e.released_at.slice(0, 10)}</span>}
          </div>
          <ul className="mt-2 space-y-1">
            {e.changes.map((c, i) => (
              <li key={i} className="text-sm">
                <span className="mr-1">{TYPE_ICONS[c.type] || "📌"}</span>{c.description}
              </li>
            ))}
          </ul>
        </div>
      ))}
      {totalPages > 1 && (
        <div className="flex justify-center gap-2">
          <button onClick={() => onPageChange(page - 1)} disabled={page <= 1}
            className="rounded border px-3 py-1 text-sm disabled:opacity-30">← Prev</button>
          <span className="px-3 py-1 text-sm">{page}/{totalPages}</span>
          <button onClick={() => onPageChange(page + 1)} disabled={page >= totalPages}
            className="rounded border px-3 py-1 text-sm disabled:opacity-30">Next →</button>
        </div>
      )}
    </div>
  );
}
