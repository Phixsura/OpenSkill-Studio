"use client";

import { useState } from "react";

interface StatusPageSubscribeProps { options: string[]; onSubscribe: (channel: string, contact: string) => void; }

const CHANNEL_ICONS: Record<string, string> = { email: "📧", slack: "💬", webhook: "🔗", rss: "📡" };

export function StatusPageSubscribe({ options, onSubscribe }: StatusPageSubscribeProps) {
  const [channel, setChannel] = useState(options[0] || "email");
  const [contact, setContact] = useState("");

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Subscribe to Updates</h3>
      <div className="mt-3 flex gap-1">
        {options.map(o => (
          <button key={o} onClick={() => setChannel(o)}
            className={`rounded px-2 py-1 text-xs ${channel === o ? "bg-blue-100 font-semibold text-blue-700" : "text-gray-500"}`}>
            {CHANNEL_ICONS[o] || "📌"} {o}
          </button>
        ))}
      </div>
      <div className="mt-3 flex gap-2">
        <input value={contact} onChange={e => setContact(e.target.value)}
          placeholder={channel === "email" ? "your@email.com" : channel === "webhook" ? "https://..." : ""}
          className="flex-1 rounded border px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
        <button onClick={() => onSubscribe(channel, contact)} disabled={!contact}
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50">Subscribe</button>
      </div>
    </div>
  );
}
