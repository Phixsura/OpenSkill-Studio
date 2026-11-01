"use client";

import { useState } from "react";

interface ResourceTagEditorProps { tags: Record<string, string>;
  onAdd: (key: string, value: string) => void; onRemove: (key: string) => void; }

export function ResourceTagEditor({ tags, onAdd, onRemove }: ResourceTagEditorProps) {
  const [key, setKey] = useState("");
  const [value, setValue] = useState("");
  const entries = Object.entries(tags);

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Tags</h2>
      <div className="flex gap-2">
        <input value={key} onChange={e => setKey(e.target.value)} placeholder="key"
          className="w-28 rounded border px-2 py-1.5 font-mono text-sm dark:border-gray-600 dark:bg-gray-700" />
        <input value={value} onChange={e => setValue(e.target.value)} placeholder="value"
          className="flex-1 rounded border px-2 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700" />
        <button onClick={() => { onAdd(key, value); setKey(""); setValue(""); }}
          className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Add</button>
      </div>
      <div className="flex flex-wrap gap-2">
        {entries.map(([k, v]) => (
          <span key={k} className="flex items-center gap-1 rounded-full border px-3 py-1 text-xs dark:border-gray-600">
            <strong>{k}</strong>={v}
            <button onClick={() => onRemove(k)} className="ml-0.5 text-red-400">×</button>
          </span>
        ))}
        {entries.length === 0 && <p className="text-sm text-gray-400">No tags</p>}
      </div>
    </div>
  );
}
