"use client";

import { useState } from "react";

interface IpAllowlistEditorProps { entries: string[]; onAdd: (entry: string) => void; onRemove: (entry: string) => void; }

export function IpAllowlistEditor({ entries, onAdd, onRemove }: IpAllowlistEditorProps) {
  const [input, setInput] = useState("");

  const handleAdd = () => { if (input.trim()) { onAdd(input.trim()); setInput(""); } };

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">IP Allowlist</h3>
      <p className="mt-1 text-xs text-gray-400">Restrict API access to specific IPs or CIDR ranges.</p>
      <div className="mt-3 flex gap-2">
        <input value={input} onChange={e => setInput(e.target.value)} placeholder="10.0.0.0/24 or 192.168.1.1"
          className="flex-1 rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700"
          onKeyDown={e => e.key === "Enter" && handleAdd()} />
        <button onClick={handleAdd} disabled={!input.trim()}
          className="rounded bg-blue-600 px-3 py-2 text-sm text-white disabled:opacity-50">Add</button>
      </div>
      {entries.length === 0 ? (
        <p className="mt-3 text-xs text-gray-400">No IP restrictions — all IPs allowed.</p>
      ) : (
        <ul className="mt-3 space-y-1">
          {entries.map(e => (
            <li key={e} className="flex items-center justify-between rounded bg-gray-50 px-3 py-1 text-sm dark:bg-gray-800">
              <code>{e}</code>
              <button onClick={() => onRemove(e)} className="text-red-500 text-xs hover:underline">Remove</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
