"use client";

interface Activity { action: string; label: string; icon: string; target: string; timestamp: string; ip: string; }
interface UserActivityLogProps { activities: Activity[]; activeDays: number; }

export function UserActivityLog({ activities, activeDays }: UserActivityLogProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Activity Log</h3>
        <span className="text-xs text-gray-400">{activeDays} active days</span>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700 max-h-64 overflow-y-auto">
        {activities.map((a, i) => (
          <div key={i} className="flex items-center gap-3 px-4 py-2.5">
            <span className="text-sm">{a.icon}</span>
            <div className="flex-1 min-w-0">
              <p className="text-sm"><strong>{a.label}</strong>{a.target && ` — ${a.target}`}</p>
              <p className="text-xs text-gray-400">{new Date(a.timestamp).toLocaleString()}{a.ip && ` · ${a.ip}`}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
