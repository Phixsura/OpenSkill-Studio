"use client";

interface TopicInfo {
  topic_id: string;
  name: string;
  subscriber_count: number;
  publish_count: number;
}

interface APIEventBusCardProps {
  topics: TopicInfo[];
  appName: string;
}

export default function APIEventBusCard({ topics, appName }: APIEventBusCardProps) {
  const totalPubs = topics.reduce((s, t) => s + t.publish_count, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📡 Event Bus</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{topics.length} topics · {totalPubs} published</span>
      </div>

      {topics.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No event topics</p>
      ) : (
        <div className="space-y-1.5">
          {topics.map((t) => (
            <div key={t.topic_id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <span className="text-xs font-medium text-gray-700 dark:text-gray-300">{t.name}</span>
              <span className="text-[10px] text-gray-400">{t.subscriber_count} subs · {t.publish_count} pubs</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
