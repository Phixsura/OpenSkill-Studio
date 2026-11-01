"use client";

interface PublishResult { channel: string; status: string; }
interface ChangelogPublisherProps { version: string; summary: string;
  changeCount: number; results: PublishResult[];
  availableChannels: string[]; onPublish: (channels: string[]) => void; }

const CH_ICONS: Record<string, string> = {
  email: "📧", slack: "💬", in_app: "🔔", rss: "📡", status_page: "📊",
};

export function ChangelogPublisher({ version, summary, changeCount, results, availableChannels, onPublish }: ChangelogPublisherProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold text-sm">📢 Publish v{version}</h3>
          <div className="text-xs text-gray-400">{summary} · {changeCount} changes</div>
        </div>
        <button onClick={() => onPublish(availableChannels)}
          className="px-3 py-1 text-xs bg-blue-500 text-white rounded-lg">Publish All</button>
      </div>
      {results.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {results.map(r => (
            <div key={r.channel} className="flex items-center justify-between px-4 py-2 text-xs">
              <span>{CH_ICONS[r.channel] ?? "📨"} {r.channel}</span>
              <span className="text-green-600">{r.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
