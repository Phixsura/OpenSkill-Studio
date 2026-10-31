"use client";

import { useState } from "react";

interface DnsRecord { type: string; name: string; value: string; }
interface DomainSetupProps { onVerify: (domain: string) => void; record: DnsRecord | null; verified: boolean; }

export function DomainSetup({ onVerify, record, verified }: DomainSetupProps) {
  const [domain, setDomain] = useState("");

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">Custom Domain</h3>
      <div className="flex gap-2">
        <input type="text" placeholder="myapp.example.com" value={domain}
          onChange={e => setDomain(e.target.value)}
          className="flex-1 rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
        <button onClick={() => domain && onVerify(domain)}
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white">Verify</button>
      </div>
      {record && !verified && (
        <div className="rounded-lg border bg-yellow-50 p-4 dark:bg-yellow-900/10 dark:border-yellow-700">
          <p className="text-sm font-medium">Add this DNS record:</p>
          <div className="mt-2 space-y-1 text-xs font-mono">
            <p><span className="text-gray-500">Type:</span> {record.type}</p>
            <p><span className="text-gray-500">Name:</span> {record.name}</p>
            <p><span className="text-gray-500">Value:</span> {record.value}</p>
          </div>
        </div>
      )}
      {verified && (
        <div className="flex items-center gap-2 rounded-lg border border-green-500 bg-green-50 p-3 dark:bg-green-900/10">
          <span>✅</span>
          <span className="text-sm font-medium text-green-700 dark:text-green-400">Domain verified!</span>
        </div>
      )}
    </div>
  );
}
