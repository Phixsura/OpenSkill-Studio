"use client";

interface ChangelogSubManagerProps { active: number; total: number;
  byChannel: Record<string, number>; currentChannel: string | null;
  onSubscribe: (channel: string) => void; onUnsubscribe: () => void; }

export function ChangelogSubManager({ active, total, byChannel, currentChannel, onSubscribe, onUnsubscribe }: ChangelogSubManagerProps) {
  const channels = ["email", "slack", "in_app"];
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📬 Changelog Subscriptions</h3>
        <span className="text-xs text-gray-400">{active} active / {total} total</span>
      </div>
      <div className="p-4">
        {currentChannel ? (
          <div className="flex items-center justify-between">
            <span className="text-sm">Subscribed via <span className="font-medium">{currentChannel}</span></span>
            <button onClick={onUnsubscribe} className="text-xs text-red-500 hover:underline">Unsubscribe</button>
          </div>
        ) : (
          <div className="flex gap-2">
            {channels.map(ch => (
              <button key={ch} onClick={() => onSubscribe(ch)}
                className="px-3 py-1.5 text-xs bg-blue-500 text-white rounded-lg capitalize">{ch.replaceAll("_", " ")}</button>
            ))}
          </div>
        )}
      </div>
      <div className="flex gap-3 px-4 py-2 border-t dark:border-gray-700 text-xs text-gray-400">
        {Object.entries(byChannel).map(([ch, count]) => (
          <span key={ch}>{ch}: {count}</span>
        ))}
      </div>
    </div>
  );
}
