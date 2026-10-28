"use client";

interface SubscriberInfo {
  subscriber_id: string;
  channel: string;
  target: string;
  release_types: string[] | null;
  active: boolean;
  notification_count: number;
}

interface ChangelogSubscriberCardProps {
  subscribers: SubscriberInfo[];
  appName: string;
}

const CHANNEL_ICONS: Record<string, string> = { email: "✉️", webhook: "🔗", in_app: "🔔" };

export default function ChangelogSubscriberCard({
  subscribers,
  appName,
}: ChangelogSubscriberCardProps) {
  const activeCount = subscribers.filter((s) => s.active).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Changelog Subscribers
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{activeCount} active</span>
      </div>

      {subscribers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No subscribers</p>
      ) : (
        <div className="space-y-2">
          {subscribers.map((s) => (
            <div
              key={s.subscriber_id}
              className={`flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800 ${!s.active ? "opacity-50" : ""}`}
            >
              <div className="flex items-center gap-2">
                <span>{CHANNEL_ICONS[s.channel] ?? "📨"}</span>
                <div>
                  <span className="text-sm text-gray-800 dark:text-gray-200">{s.target}</span>
                  <div className="flex items-center gap-2 text-[11px] text-gray-400">
                    {s.release_types ? (
                      <span>{s.release_types.join(", ")}</span>
                    ) : (
                      <span>all releases</span>
                    )}
                    {!s.active && <span className="text-red-400">unsubscribed</span>}
                  </div>
                </div>
              </div>
              <span className="text-[11px] text-gray-400">{s.notification_count} sent</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
