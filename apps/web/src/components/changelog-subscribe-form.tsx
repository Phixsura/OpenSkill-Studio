"use client";

import { useState } from "react";

interface ChangelogSubscribeFormProps { appName: string; channels: string[];
  onSubscribe: (email: string, channels: string[]) => void; }

export function ChangelogSubscribeForm({ appName, channels, onSubscribe }: ChangelogSubscribeFormProps) {
  const [email, setEmail] = useState("");
  const [selected, setSelected] = useState<Set<string>>(new Set(["email"]));

  const toggle = (ch: string) => {
    const next = new Set(selected);
    next.has(ch) ? next.delete(ch) : next.add(ch);
    setSelected(next);
  };

  return (
    <div className="rounded-xl border p-4 dark:border-gray-700">
      <h3 className="text-sm font-semibold">📬 Subscribe to {appName} Updates</h3>
      <div className="mt-3 space-y-2">
        <input type="email" value={email} onChange={e => setEmail(e.target.value)}
          placeholder="your@email.com"
          className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
        <div className="flex gap-2">
          {channels.map(ch => (
            <label key={ch} className="flex items-center gap-1.5 text-xs">
              <input type="checkbox" checked={selected.has(ch)} onChange={() => toggle(ch)} className="accent-blue-600" />
              <span className="capitalize">{ch}</span>
            </label>
          ))}
        </div>
        <button onClick={() => email && selected.size > 0 && onSubscribe(email, Array.from(selected))}
          className="w-full rounded bg-blue-600 py-2 text-sm text-white">Subscribe</button>
      </div>
    </div>
  );
}
