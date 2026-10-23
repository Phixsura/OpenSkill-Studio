"use client";
import { useState } from "react";

interface IpRule { cidr: string; label: string; enabled: boolean; hosts: number; }
interface IpAllowlistEditorProps { rules: IpRule[]; onAdd: (cidr: string, label: string) => void;
  onRemove: (cidr: string) => void; }

export function IpAllowlistEditor({ rules, onAdd, onRemove }: IpAllowlistEditorProps) {
  const [cidr, setCidr] = useState("");
  const [label, setLabel] = useState("");

  const handleAdd = () => {
    if (cidr.trim()) { onAdd(cidr.trim(), label.trim()); setCidr(""); setLabel(""); }
  };

  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🛡️ IP Allowlist</h3>
      <div className="space-y-2 mb-4">
        {rules.map(r => (
          <div key={r.cidr} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
            <div>
              <span className="text-sm font-mono">{r.cidr}</span>
              {r.label && <span className="text-xs text-gray-400 ml-2">{r.label}</span>}
              <span className="text-xs text-gray-400 ml-2">({r.hosts.toLocaleString()} hosts)</span>
            </div>
            <button onClick={() => onRemove(r.cidr)} className="text-xs text-red-500 hover:text-red-700">Remove</button>
          </div>
        ))}
        {rules.length === 0 && <p className="text-sm text-gray-400">No rules — all IPs allowed</p>}
      </div>
      <div className="flex gap-2">
        <input value={cidr} onChange={e => setCidr(e.target.value)} placeholder="10.0.0.0/8"
          className="flex-1 text-sm font-mono px-2 py-1.5 border rounded dark:bg-gray-800 dark:border-gray-600" />
        <input value={label} onChange={e => setLabel(e.target.value)} placeholder="Label"
          className="w-32 text-sm px-2 py-1.5 border rounded dark:bg-gray-800 dark:border-gray-600" />
        <button onClick={handleAdd}
          className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">Add</button>
      </div>
    </div>
  );
}
