"use client";

interface CalendarEvent { title: string; date: string; type: string; icon: string; description: string; }
interface EventCalendarProps { events: CalendarEvent[]; total: number; }

export function EventCalendar({ events, total }: EventCalendarProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📅 Upcoming Events</h3>
        <span className="text-xs text-gray-400">{total} events</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {events.map((e, i) => (
          <div key={i} className="flex gap-3 px-4 py-3">
            <div className="text-center shrink-0 w-12">
              <p className="text-xs text-gray-400">{e.date.slice(5, 7)}/{e.date.slice(8)}</p>
              <p className="text-lg">{e.icon}</p>
            </div>
            <div>
              <p className="text-sm font-medium">{e.title}</p>
              {e.description && <p className="text-xs text-gray-500">{e.description}</p>}
              <span className="text-xs text-gray-400 capitalize">{e.type}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
