"use client";

interface Channel { channel: string; version: string; released_at: string; }
interface ReleaseChannelSelectorProps { channels: Channel[]; selected: string; onSelect: (ch: string) => void; }

const CHANNEL_STYLES: Record<string, { color: string; label: string }> = {
  stable: { color: "bg-green-100 text-green-800", label: "Stable" },
  rc: { color: "bg-blue-100 text-blue-800", label: "Release Candidate" },
  beta: { color: "bg-yellow-100 text-yellow-800", label: "Beta" },
  canary: { color: "bg-orange-100 text-orange-800", label: "Canary" },
};

export function ReleaseChannelSelector({ channels, selected, onSelect }: ReleaseChannelSelectorProps) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">Release Channel</label>
      <div className="flex flex-wrap gap-2">
        {channels.map(ch => {
          const style = CHANNEL_STYLES[ch.channel] || { color: "bg-gray-100", label: ch.channel };
          const isSelected = ch.channel === selected;
          return (
            <button key={ch.channel} onClick={() => onSelect(ch.channel)}
              className={`rounded-lg border px-3 py-2 text-sm transition ${isSelected ? "border-blue-500 ring-2 ring-blue-200" : "border-gray-200 dark:border-gray-700"}`}>
              <span className={`mr-1 inline-block rounded px-1.5 py-0.5 text-xs ${style.color}`}>{style.label}</span>
              <span className="font-mono text-xs">{ch.version}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
