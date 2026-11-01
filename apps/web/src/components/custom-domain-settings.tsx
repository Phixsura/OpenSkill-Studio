"use client";
import { useState } from "react";

interface Domain { domain: string; verified: boolean; sslActive: boolean; verificationToken: string; }

export function CustomDomainSettings({ domains, onAdd, onRemove }: {
  domains: Domain[]; onAdd?: (domain: string) => void; onRemove?: (domain: string) => void;
}) {
  const [newDomain, setNewDomain] = useState("");
  return (
    <div className="space-y-3">
      <h3 className="font-bold text-sm">Custom Domains</h3>
      <div className="flex gap-2">
        <input value={newDomain} onChange={e => setNewDomain(e.target.value)} placeholder="docs.yourapp.com"
          className="flex-1 border dark:border-gray-700 rounded-lg px-3 py-2 text-sm bg-transparent" />
        <button onClick={() => { onAdd?.(newDomain); setNewDomain(""); }}
          className="bg-blue-500 text-white px-3 py-2 rounded-lg text-sm">Add</button>
      </div>
      {domains.map(d => (
        <div key={d.domain} className="border dark:border-gray-700 rounded-xl p-3 flex items-center justify-between">
          <div>
            <span className="font-mono text-sm">{d.domain}</span>
            <div className="flex gap-2 mt-1">
              <span className={`text-xs px-1.5 py-0.5 rounded ${d.verified ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
                {d.verified ? "✅ Verified" : "⏳ Pending"}
              </span>
              {d.sslActive && <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">🔒 SSL</span>}
            </div>
            {!d.verified && <code className="text-[10px] text-gray-400 block mt-1">TXT: {d.verificationToken.slice(0, 20)}...</code>}
          </div>
          <button onClick={() => onRemove?.(d.domain)} className="text-xs text-red-400">Remove</button>
        </div>
      ))}
    </div>
  );
}
