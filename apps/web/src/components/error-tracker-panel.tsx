"use client";
interface ErrorGroup { group: string; count: number; }
interface ErrorTrackerPanelProps { groups: ErrorGroup[]; totalErrors: number; uniqueGroups: number; }
export function ErrorTrackerPanel({ groups, totalErrors, uniqueGroups }: ErrorTrackerPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🐛 Error Tracker</h3>
        <span className="text-xs text-gray-400">{totalErrors} errors · {uniqueGroups} groups</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {groups.map(g => (
          <div key={g.group} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono truncate max-w-[250px] text-red-500">{g.group}</span>
            <span className="text-gray-400 font-bold">{g.count}x</span>
          </div>
        ))}
      </div>
    </div>
  );
}
