"use client";

interface Revision { revision: string; author: string; message: string; size: number; }
interface ContentRevisionListProps { revisions: Revision[]; total: number;
  authorCount: number; onRestore: (rev: string) => void; }

export function ContentRevisionList({ revisions, total, authorCount, onRestore }: ContentRevisionListProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📝 Revisions</h3>
        <span className="text-xs text-gray-400">{total} revisions · {authorCount} authors</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {revisions.map((r, i) => (
          <div key={r.revision} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-blue-500">{r.revision}</span>
                {i === 0 && <span className="text-[10px] text-green-600">latest</span>}
              </div>
              <div className="text-[10px] text-gray-400">{r.author}{r.message ? ` — ${r.message}` : ""}</div>
            </div>
            {i > 0 && (
              <button onClick={() => onRestore(r.revision)}
                className="text-xs text-blue-500 hover:underline">Restore</button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
