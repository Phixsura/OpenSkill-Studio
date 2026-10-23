"use client";

import { useState } from "react";

interface DnsRecord { type: string; name: string; value: string; }
interface SslStatus { status: string; issuer: string; autoRenew: boolean; }
interface CustomDomainSetupProps { domain: string | null; status: string | null;
  dnsRecords: DnsRecord[]; ssl: SslStatus | null; statusIcon: string;
  statusMessage: string; onSetup: (domain: string) => void; onVerify: () => void; }

export function CustomDomainSetup({ domain, status, dnsRecords, ssl, statusIcon,
  statusMessage, onSetup, onVerify }: CustomDomainSetupProps) {
  const [input, setInput] = useState("");
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">🌐 Custom Domain</h3>
      {!domain ? (
        <div className="flex gap-2">
          <input value={input} onChange={e => setInput(e.target.value)} placeholder="myapp.example.com"
            className="flex-1 rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
          <button onClick={() => input && onSetup(input)} className="rounded bg-blue-600 px-4 py-2 text-sm text-white">Setup</button>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span>{statusIcon}</span>
            <code className="text-sm font-mono font-bold">{domain}</code>
            <span className="text-xs text-gray-400">{statusMessage}</span>
          </div>
          {status === "pending_verification" && (
            <>
              <div className="rounded-lg bg-yellow-50 p-3 dark:bg-yellow-900/10">
                <p className="text-xs font-semibold mb-2">Add these DNS records:</p>
                {dnsRecords.map((r, i) => (
                  <div key={i} className="text-xs font-mono mb-1">
                    <span className="text-blue-600">{r.type}</span> {r.name} → {r.value}
                  </div>
                ))}
              </div>
              <button onClick={onVerify} className="rounded bg-blue-600 px-4 py-2 text-sm text-white">Verify DNS</button>
            </>
          )}
          {ssl && <p className="text-xs text-gray-400">SSL: {ssl.issuer} · Auto-renew: {ssl.autoRenew ? "✓" : "✗"}</p>}
        </div>
      )}
    </div>
  );
}
