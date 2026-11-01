"use client";

interface MilestoneInfo {
  milestone_id: string;
  title: string;
  milestone_type: "release" | "feature" | "fix" | "breaking";
  version: string;
}

interface ChangelogTimelineCardProps {
  milestones: MilestoneInfo[];
  totalCount: number;
  appName: string;
}

const typeIcon: Record<string, string> = { release: "🚀", feature: "✨", fix: "🐛", breaking: "💥" };

export default function ChangelogTimelineCard({ milestones, totalCount, appName }: ChangelogTimelineCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📅 Changelog Timeline</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{totalCount} milestones</span>
      </div>

      {milestones.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No milestones</p>
      ) : (
        <div className="space-y-1">
          {milestones.map((m) => (
            <div key={m.milestone_id} className="flex items-center gap-2 text-[11px]">
              <span>{typeIcon[m.milestone_type]}</span>
              <span className="text-gray-700 dark:text-gray-300">{m.title}</span>
              {m.version && <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{m.version}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
