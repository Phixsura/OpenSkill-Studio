"use client";

interface MilestoneInfo { milestone_id: string; title: string; version: string; pinned: boolean; }

interface APIChangelogMilestoneCardProps { milestones: MilestoneInfo[]; appName: string; }

export default function APIChangelogMilestoneCard({ milestones, appName }: APIChangelogMilestoneCardProps) {
  const pinnedCount = milestones.filter((m) => m.pinned).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏆 Milestones</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{pinnedCount} pinned / {milestones.length} total</span>
      </div>
      {milestones.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No milestones</p>
      ) : (
        <div className="space-y-1">
          {milestones.map((m) => (
            <div key={m.milestone_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                {m.pinned && <span className="text-yellow-500">📌</span>}
                <span className="text-gray-700 dark:text-gray-300">{m.title}</span>
              </div>
              <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{m.version}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
