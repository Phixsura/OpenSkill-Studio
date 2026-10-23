"use client";

import { useState } from "react";

interface ChangelogEntryFormProps { onSubmit: (entry: { type: string; title: string; description: string }) => void; }

const types = [
  { id: "added", label: "Added", icon: "✨" },
  { id: "changed", label: "Changed", icon: "🔄" },
  { id: "fixed", label: "Fixed", icon: "🐛" },
  { id: "removed", label: "Removed", icon: "🗑️" },
  { id: "security", label: "Security", icon: "🔒" },
  { id: "performance", label: "Performance", icon: "⚡" },
];

export function ChangelogEntryForm({ onSubmit }: ChangelogEntryFormProps) {
  const [type, setType] = useState("added");
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState("");

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">Add Changelog Entry</h3>
      <div className="flex flex-wrap gap-1">
        {types.map(t => (
          <button key={t.id} onClick={() => setType(t.id)}
            className={`rounded px-2 py-1 text-xs ${type === t.id ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>
            {t.icon} {t.label}
          </button>
        ))}
      </div>
      <input value={title} onChange={e => setTitle(e.target.value)} placeholder="What changed?"
        className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
      <textarea value={desc} onChange={e => setDesc(e.target.value)} placeholder="Details (optional)" rows={2}
        className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
      <button onClick={() => { if (title) { onSubmit({ type, title, description: desc }); setTitle(""); setDesc(""); } }}
        className="rounded bg-blue-600 px-4 py-2 text-sm text-white">Add Entry</button>
    </div>
  );
}
