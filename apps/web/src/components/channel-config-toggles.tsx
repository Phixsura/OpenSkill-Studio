"use client";

interface Channel { id: string; label: string; icon: string; enabled: boolean; }
interface ChannelConfigTogglesProps { channels: Channel[]; enabledCount: number;
  onToggle: (id: string) => void; }

export function ChannelConfigToggles({ channels, enabledCount, onToggle }: ChannelConfigTogglesProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">📬 Notification Channels</h3>
        <span className="text-xs text-gray-400">{enabledCount} active</span>
      </div>
      <div className="space-y-2">
        {channels.map(c => (
          <div key={c.id} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span>{c.icon}</span>
              <span className="text-sm font-medium">{c.label}</span>
            </div>
            <button onClick={() => onToggle(c.id)}
              className={`w-9 h-5 rounded-full ${c.enabled ? "bg-green-500" : "bg-gray-300 dark:bg-gray-600"}`}>
              <span className={`block w-4 h-4 rounded-full bg-white transform ${c.enabled ? "translate-x-4" : "translate-x-0.5"}`} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
