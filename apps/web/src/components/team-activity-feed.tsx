"use client";

interface Activity { actor: string; action: string; icon: string; target: string; timestamp: string; }
interface Contributor { name: string; count: number; }
interface TeamActivityFeedProps { activities: Activity[]; topContributors: Contributor[]; uniqueMembers: number; }

export function TeamActivityFeed({ activities, topContributors, uniqueMembers }: TeamActivityFeedProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Team Activity</h3>
        <span className="text-xs text-gray-400">{uniqueMembers} members active</span>
      </div>
      <div className="flex gap-2 overflow-x-auto">
        {topContributors.map(c => (
          <div key={c.name} className="shrink-0 rounded-lg border px-3 py-1.5 text-center dark:border-gray-700">
            <p className="text-xs font-medium">{c.name}</p>
            <p className="text-xs text-gray-400">{c.count} actions</p>
          </div>
        ))}
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700 max-h-56 overflow-y-auto">
        {activities.map((a, i) => (
          <div key={i} className="flex items-center gap-2 px-4 py-2">
            <span className="text-xs">{a.icon}</span>
            <span className="text-sm"><strong>{a.actor}</strong> {a.action} <span className="text-gray-500">{a.target}</span></span>
          </div>
        ))}
      </div>
    </div>
  );
}
