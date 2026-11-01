"use client";

interface TimelineEvent {
  id: string;
  type: "publish" | "install" | "review" | "update" | "incident" | "billing";
  title: string;
  description: string;
  timestamp: string;
  actor: string;
  metadata?: Record<string, string>;
}

const typeConfig: Record<string, { icon: string; color: string }> = {
  publish: { icon: "📦", color: "border-green-500" },
  install: { icon: "⬇️", color: "border-blue-500" },
  review: { icon: "⭐", color: "border-yellow-500" },
  update: { icon: "🔄", color: "border-purple-500" },
  incident: { icon: "🚨", color: "border-red-500" },
  billing: { icon: "💰", color: "border-emerald-500" },
};

export function ExtensionEventTimeline({
  events,
  extensionName,
}: {
  events: TimelineEvent[];
  extensionName: string;
}) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📅 {extensionName} Timeline</h2>

      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700" />

        <div className="space-y-4">
          {events.map((event) => {
            const cfg = typeConfig[event.type] || { icon: "📌", color: "border-gray-400" };
            return (
              <div key={event.id} className="relative flex gap-4 pl-10">
                {/* Dot on timeline */}
                <div className={`absolute left-2.5 w-3 h-3 rounded-full border-2 bg-white dark:bg-gray-900 ${cfg.color}`} />

                <div className="flex-1 rounded-lg border dark:border-gray-700 p-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <span>{cfg.icon}</span>
                      <span className="font-medium text-sm">{event.title}</span>
                      <span className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">
                        {event.type}
                      </span>
                    </div>
                    <span className="text-xs text-gray-400">{event.timestamp}</span>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">{event.description}</p>
                  <div className="flex gap-2 mt-1 text-xs text-gray-400">
                    <span>by {event.actor}</span>
                    {event.metadata && Object.entries(event.metadata).map(([k, v]) => (
                      <span key={k} className="bg-gray-50 dark:bg-gray-800 px-1.5 py-0.5 rounded">
                        {k}: {v}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
