"use client";

interface ErrorGroup { fingerprint: string; type: string; message: string; count: number; }
interface ErrorGroupListProps { groups: ErrorGroup[]; uniqueErrors: number;
  totalOccurrences: number; dedupRatio: number; }

export function ErrorGroupList({ groups, uniqueErrors, totalOccurrences, dedupRatio }: ErrorGroupListProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🐛 Error Groups</h3>
        <span className="text-xs text-gray-400">{uniqueErrors} unique / {totalOccurrences} total · {dedupRatio}x dedup</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {groups.map(g => (
          <div key={g.fingerprint} className="px-4 py-2.5">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-red-600">{g.type}</span>
              <span className="px-2 py-0.5 text-[10px] bg-red-100 text-red-700 rounded-full">{g.count}×</span>
            </div>
            <div className="text-xs text-gray-500 mt-0.5 truncate">{g.message}</div>
            <div className="text-[10px] text-gray-300 font-mono mt-0.5">{g.fingerprint}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
