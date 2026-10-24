"use client";
import { useState } from "react";

interface IpFilterEditorProps { allowlist: string[]; platformIps: string[];
  onAdd: (ip: string) => void; onRemove: (ip: string) => void; onAddPlatform: () => void; }

export function IpFilterEditor({ allowlist, platformIps, onAdd, onRemove, onAddPlatform }: IpFilterEditorProps) {
  const [ip, setIp] = useState("");
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🛡️ IP Filter</h3>
      <div className="space-y-1 mb-3">
        {allowlist.map(a => (
          <div key={a} className="flex justify-between text-sm bg-gray-50 dark:bg-gray-800 rounded px-3 py-1.5">
            <span className="font-mono text-xs">{a}</span>
            <button onClick={() => onRemove(a)} className="text-xs text-red-500">×</button>
          </div>
        ))}
        {allowlist.length === 0 && <p className="text-xs text-gray-400">No filter — all IPs allowed</p>}
      </div>
      <div className="flex gap-2 mb-2">
        <input value={ip} onChange={e => setIp(e.target.value)} placeholder="10.0.0.0/8"
          className="flex-1 text-sm font-mono px-2 py-1 border rounded dark:bg-gray-800 dark:border-gray-600" />
        <button onClick={() => { if (ip) { onAdd(ip); setIp(""); } }}
          className="text-xs px-3 py-1 bg-blue-600 text-white rounded">Add</button>
      </div>
      <button onClick={onAddPlatform} className="text-xs text-blue-600 hover:text-blue-700">
        + Add OpenSkill platform IPs ({platformIps.length})
      </button>
    </div>
  );
}
