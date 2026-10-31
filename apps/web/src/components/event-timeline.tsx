"use client";

interface TimelineEvent { type: string; icon: string; title: string; description: string; timestamp: string; actor?: string; }

interface EventTimelineProps { events: TimelineEvent[]; }

export function EventTimeline({ events }: EventTimelineProps) {
  if (events.length === 0) return <p className="text-sm text-gray-400">No activity yet.</p>;
  return (
    <div className="space-y-0">
      {events.map((e, i) => (
        <div key={i} className="flex gap-3 pb-4">
          <div className="flex flex-col items-center">
            <span className="text-lg">{e.icon}</span>
            {i < events.length - 1 && <div className="mt-1 w-px flex-1 bg-gray-200 dark:bg-gray-700" />}
          </div>
          <div className="flex-1 pb-2">
            <p className="text-sm font-medium">{e.title}</p>
            {e.description && <p className="text-xs text-gray-500">{e.description}</p>}
            <p className="mt-1 text-xs text-gray-400">
              {e.actor && <span>{e.actor} · </span>}
              {new Date(e.timestamp).toLocaleDateString()}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
