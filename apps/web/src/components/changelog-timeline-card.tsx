"use client";

interface TimelineEventInfo {
  event_id: string;
  event_type: "release" | "incident" | "deployment" | "maintenance" | "config_change";
  title: string;
  timestamp: string;
}

interface ChangelogTimelineCardProps {
  events: TimelineEventInfo[];
  appName: string;
}

const TYPE_STYLES: Record<string, { icon: string; color: string }> = {
  release: { icon: "🚀", color: "border-green-400" },
  incident: { icon: "🔥", color: "border-red-400" },
  deployment: { icon: "📦", color: "border-blue-400" },
  maintenance: { icon: "🔧", color: "border-yellow-400" },
  config_change: { icon: "⚙️", color: "border-purple-400" },
};

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

export default function ChangelogTimelineCard({ events, appName }: ChangelogTimelineCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Timeline</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{events.length} events</span>
      </div>

      {events.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No events</p>
      ) : (
        <div className="space-y-0">
          {events.map((e, i) => {
            const st = TYPE_STYLES[e.event_type] ?? TYPE_STYLES.release;
            return (
              <div key={e.event_id} className="flex gap-3">
                <div className="flex flex-col items-center">
                  <span className="text-sm">{st.icon}</span>
                  {i < events.length - 1 && (
                    <div className="h-full w-px bg-gray-200 dark:bg-gray-700" />
                  )}
                </div>
                <div className="pb-4">
                  <span className="text-sm text-gray-800 dark:text-gray-200">{e.title}</span>
                  <p className="text-[11px] text-gray-400">{timeAgo(e.timestamp)}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
