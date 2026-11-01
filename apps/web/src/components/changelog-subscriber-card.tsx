"use client";

interface SubscriberInfo {
  subscriber_id: string;
  email: string;
  name: string;
  active: boolean;
  delivery_count: number;
}

interface ChangelogSubscriberCardProps {
  subscribers: SubscriberInfo[];
  activeCount: number;
  appName: string;
}

export default function ChangelogSubscriberCard({
  subscribers,
  activeCount,
  appName,
}: ChangelogSubscriberCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            📬 Changelog Subscribers
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{activeCount} active</span>
      </div>

      {subscribers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No subscribers</p>
      ) : (
        <div className="space-y-1">
          {subscribers.map((s) => (
            <div
              key={s.subscriber_id}
              className={`flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800 ${!s.active ? "opacity-50" : ""}`}
            >
              <div className="flex items-center gap-2">
                <span
                  className={`h-1.5 w-1.5 rounded-full ${s.active ? "bg-green-500" : "bg-gray-400"}`}
                />
                <span className="text-xs text-gray-700 dark:text-gray-300">
                  {s.name || s.email}
                </span>
              </div>
              <span className="text-[10px] text-gray-400">{s.delivery_count} sent</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
