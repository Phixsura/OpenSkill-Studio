"use client";

interface ScheduledItem { title: string; content_type: string; publish_at: string; status: string; }
interface ContentScheduleCalendarProps { dates: Record<string, ScheduledItem[]>; totalScheduled: number;
  onEdit: (title: string) => void; }

const typeIcon: Record<string, string> = {
  blog_post: "📝", changelog: "📋", announcement: "📢", newsletter: "📧", release: "🚀",
};

export function ContentScheduleCalendar({ dates, totalScheduled, onEdit }: ContentScheduleCalendarProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Content Schedule</h2>
        <span className="text-xs text-gray-400">{totalScheduled} scheduled</span>
      </div>
      {Object.entries(dates).map(([date, items]) => (
        <div key={date}>
          <h3 className="text-sm font-medium text-gray-500">{new Date(date).toLocaleDateString(undefined, { weekday: "long", month: "short", day: "numeric" })}</h3>
          <div className="mt-1 space-y-1">
            {items.map((item, i) => (
              <button key={i} onClick={() => onEdit(item.title)}
                className="flex w-full items-center gap-2 rounded border px-3 py-2 text-left hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
                <span>{typeIcon[item.content_type] ?? "📄"}</span>
                <span className="flex-1 text-sm">{item.title}</span>
                <span className="text-xs text-gray-400">{item.publish_at.slice(11, 16)}</span>
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
