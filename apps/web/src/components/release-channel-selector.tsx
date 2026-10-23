"use client";

interface Channel { id: string; label: string; icon: string; current_version: string | null; has_release: boolean; risk: string; }
interface ReleaseChannelSelectorProps { channels: Channel[]; selectedChannel: string; onSelect: (id: string) => void; }

const riskLabel: Record<string, string> = { low: "Stable", medium: "Pre-release", high: "Experimental" };

export function ReleaseChannelSelector({ channels, selectedChannel, onSelect }: ReleaseChannelSelectorProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Release Channels</h2>
      <div className="grid gap-2 sm:grid-cols-2">
        {channels.map(ch => (
          <button key={ch.id} onClick={() => onSelect(ch.id)}
            className={`rounded-lg border p-3 text-left ${ch.id === selectedChannel ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "border-gray-200 dark:border-gray-700"}`}>
            <div className="flex items-center gap-2">
              <span className="text-lg">{ch.icon}</span>
              <span className="font-medium">{ch.label}</span>
            </div>
            <p className="mt-1 text-xs text-gray-400">
              {ch.has_release ? `v${ch.current_version}` : "No release"} · {riskLabel[ch.risk] ?? ch.risk}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
}
