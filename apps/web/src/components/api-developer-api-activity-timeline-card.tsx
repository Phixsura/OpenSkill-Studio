"use client";

interface ActivityInfo { event_id: string; actor: string; action: string; resource: string; }
interface Props { events: ActivityInfo[]; totalCount: number; appName: string; }

export default function APIDeveloperAPIActivityTimelineCard({ events, totalCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📅 Activity Timeline</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{totalCount} events</span>
      </div>
      {events.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No activity</p>
      ) : (
        <div className="space-y-1">
          {events.map((e) => (
            <div key={e.event_id} className="flex items-center gap-2 text-[11px]">
              <span className="h-1.5 w-1.5 rounded-full bg-blue-500" />
              <span className="text-gray-500">{e.actor}</span>
              <span className="text-gray-700 dark:text-gray-300">{e.action}</span>
              <span className="text-gray-400">{e.resource}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
