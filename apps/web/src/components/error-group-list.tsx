"use client";

interface ErrorGroup { fingerprint: string; message: string; count: number;
  affectedUsers: number; lastSeen: string; }
interface ErrorGroupListProps { groups: ErrorGroup[]; totalErrors: number;
  uniqueGroups: number; onSelect: (fp: string) => void; }

export function ErrorGroupList({ groups, totalErrors, uniqueGroups, onSelect }: ErrorGroupListProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🐛 Error Groups</h3>
        <div className="flex gap-2 text-xs text-gray-400">
          <span>{totalErrors} errors</span>
          <span>{uniqueGroups} groups</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {groups.map(g => (
          <button key={g.fingerprint} onClick={() => onSelect(g.fingerprint)}
            className="w-full text-left px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-red-600 truncate max-w-md">{g.message}</span>
              <span className="text-sm font-bold ml-2">{g.count}×</span>
            </div>
            <div className="flex gap-3 text-xs text-gray-400">
              <span>👥 {g.affectedUsers} users</span>
              <span>Last: {g.lastSeen}</span>
              <span className="font-mono">{g.fingerprint}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
