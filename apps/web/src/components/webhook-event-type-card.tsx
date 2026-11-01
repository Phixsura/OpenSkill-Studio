"use client";

interface EventTypeInfo {
  event_type: string;
  description: string;
  category: string;
  emit_count: number;
}

interface WebhookEventTypeCardProps {
  eventTypes: EventTypeInfo[];
  categories: string[];
  appName: string;
}

export default function WebhookEventTypeCard({
  eventTypes,
  categories,
  appName,
}: WebhookEventTypeCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Event Types</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {eventTypes.length} types · {categories.length} categories
        </span>
      </div>

      {eventTypes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No event types</p>
      ) : (
        <div className="space-y-1">
          {eventTypes.map((e) => (
            <div
              key={e.event_type}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800"
            >
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                  {e.event_type}
                </span>
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">
                  {e.category}
                </span>
              </div>
              <span className="text-[10px] text-gray-400">{e.emit_count} emitted</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
