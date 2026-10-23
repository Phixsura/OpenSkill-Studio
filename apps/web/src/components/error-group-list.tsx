"use client";

interface ErrorGroup { fingerprint: string; type: string; message: string; count: number; first_seen: string; last_seen: string; }
interface ErrorGroupListProps { groups: ErrorGroup[]; onSelect: (fp: string) => void; }

export function ErrorGroupList({ groups, onSelect }: ErrorGroupListProps) {
  if (groups.length === 0) return <p className="text-sm text-gray-400">No errors 🎉</p>;
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="border-b p-3 dark:border-gray-700">
        <h3 className="text-sm font-semibold">Error Groups ({groups.length})</h3>
      </div>
      <ul className="max-h-64 overflow-y-auto">
        {groups.map(g => (
          <li key={g.fingerprint} onClick={() => onSelect(g.fingerprint)}
            className="cursor-pointer border-b px-3 py-2 hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-red-600">{g.type}</span>
              <span className="rounded bg-red-100 px-1.5 py-0.5 text-xs font-bold text-red-700">{g.count}</span>
            </div>
            <p className="truncate text-xs text-gray-500">{g.message}</p>
            <p className="text-xs text-gray-400">First: {g.first_seen?.slice(0, 10)} · Last: {g.last_seen?.slice(0, 10)}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
