"use client";

import { useState } from "react";

interface ChangelogSubscriptionFormProps { appName: string; availableChannels: string[];
  onSubscribe: (channels: string[]) => void; }

const channelIcons: Record<string, string> = {
  email: "📧", push: "🔔", slack: "💬", webhook: "🔗", rss: "📡",
};

export function ChangelogSubscriptionForm({ appName, availableChannels, onSubscribe }: ChangelogSubscriptionFormProps) {
  const [selected, setSelected] = useState<Set<string>>(new Set(["email"]));
  const toggle = (ch: string) => {
    const next = new Set(selected);
    next.has(ch) ? next.delete(ch) : next.add(ch);
    setSelected(next);
  };

  return (
    <div className="rounded-lg border p-4 dark:border-gray-700">
      <h3 className="font-semibold">Subscribe to {appName} Updates</h3>
      <p className="mt-1 text-xs text-gray-400">Get notified when new versions are released</p>
      <div className="mt-3 flex flex-wrap gap-2">
        {availableChannels.map(ch => (
          <button key={ch} onClick={() => toggle(ch)}
            className={`flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm ${selected.has(ch) ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "dark:border-gray-600"}`}>
            <span>{channelIcons[ch] ?? "📌"}</span>
            <span className="capitalize">{ch}</span>
          </button>
        ))}
      </div>
      <button onClick={() => onSubscribe([...selected])} disabled={selected.size === 0}
        className="mt-3 w-full rounded bg-blue-600 py-2 text-sm font-medium text-white disabled:opacity-50">
        Subscribe ({selected.size} channel{selected.size !== 1 ? "s" : ""})
      </button>
    </div>
  );
}
