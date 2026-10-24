"use client";

interface NotifStats { channel: string; count: number; }
interface NotifHubPanelProps { totalSent: number; byChannel: NotifStats[]; usersWithPrefs: number; }

export function NotifHubPanel({ totalSent, byChannel, usersWithPrefs }: NotifHubPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔔 Notification Hub</h3>
        <span className="text-xs text-gray-400">{totalSent.toLocaleString()} sent · {usersWithPrefs} users</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {byChannel.map(c => (
          <div key={c.channel} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-semibold">{c.channel}</span>
            <span className="text-gray-400">{c.count.toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
