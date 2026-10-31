"use client";
import { useState } from "react";

interface IpRule { ruleId: string; network: string; description: string; }

export function IpAllowlistEditor({ rules, onAdd, onRemove }: {
  rules: IpRule[]; onAdd?: (cidr: string, desc: string) => void; onRemove?: (ruleId: string) => void;
}) {
  const [cidr, setCidr] = useState("");
  const [desc, setDesc] = useState("");

  return (
    <div className="space-y-3">
      <h3 className="font-bold text-sm">IP Allowlist</h3>
      <div className="flex gap-2">
        <input value={cidr} onChange={e => setCidr(e.target.value)} placeholder="192.168.1.0/24"
          className="flex-1 border dark:border-gray-700 rounded-lg px-3 py-2 text-sm bg-transparent font-mono" />
        <input value={desc} onChange={e => setDesc(e.target.value)} placeholder="Description"
          className="flex-1 border dark:border-gray-700 rounded-lg px-3 py-2 text-sm bg-transparent" />
        <button onClick={() => { onAdd?.(cidr, desc); setCidr(""); setDesc(""); }}
          className="bg-blue-500 text-white px-3 py-2 rounded-lg text-sm">Add</button>
      </div>
      {rules.length === 0 ? (
        <div className="text-xs text-yellow-600 bg-yellow-50 dark:bg-yellow-900/10 rounded-lg p-3">
          ⚠️ No IP restrictions — all IPs are allowed
        </div>
      ) : (
        <div className="space-y-1">
          {rules.map(r => (
            <div key={r.ruleId} className="flex items-center justify-between border dark:border-gray-700 rounded-lg p-2 text-sm">
              <div className="flex items-center gap-2">
                <code className="text-xs font-mono bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{r.network}</code>
                {r.description && <span className="text-xs text-gray-500">{r.description}</span>}
              </div>
              <button onClick={() => onRemove?.(r.ruleId)} className="text-xs text-red-400">Remove</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
