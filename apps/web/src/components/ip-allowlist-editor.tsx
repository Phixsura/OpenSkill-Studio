"use client";

import { useState } from "react";

interface IpEntry { entry: string; normalized: string; version: number; num_addresses: number; }
interface IpAllowlistEditorProps { entries: IpEntry[]; onAdd: (entry: string) => void; onRemove: (entry: string) => void; }

export function IpAllowlistEditor({ entries, onAdd, onRemove }: IpAllowlistEditorProps) {
  const [newIp, setNewIp] = useState("");
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">IP Allowlist</h2>
      <div className="flex gap-2">
        <input value={newIp} onChange={e => setNewIp(e.target.value)} placeholder="e.g. 10.0.0.0/8"
          className="flex-1 rounded border px-3 py-1.5 font-mono text-sm dark:border-gray-600 dark:bg-gray-700" />
        <button onClick={() => { onAdd(newIp); setNewIp(""); }}
          className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Add</button>
      </div>
      {entries.length === 0 ? (
        <p className="text-sm text-gray-400">No IP restrictions — all IPs allowed</p>
      ) : (
        <div className="space-y-1.5">
          {entries.map(e => (
            <div key={e.entry} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
              <div>
                <span className="font-mono text-sm">{e.normalized}</span>
                <span className="ml-2 text-xs text-gray-400">IPv{e.version} · {e.num_addresses.toLocaleString()} addr</span>
              </div>
              <button onClick={() => onRemove(e.entry)} className="text-xs text-red-500">Remove</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
