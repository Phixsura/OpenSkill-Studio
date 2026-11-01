"use client";

import { useState } from "react";

interface DomainInfo { domain: string; sslStatus: string; dnsVerified: boolean; }

const SSL_COLOR: Record<string, string> = {
  active: "text-green-600 dark:text-green-400",
  provisioning: "text-blue-600 dark:text-blue-400",
  pending: "text-amber-600 dark:text-amber-400",
  failed: "text-red-600 dark:text-red-400",
};

export default function CustomDomainCard() {
  const [domains] = useState<DomainInfo[]>([
    { domain: "api.acme.com", sslStatus: "active", dnsVerified: true },
    { domain: "developer.acme.com", sslStatus: "provisioning", dnsVerified: true },
    { domain: "staging-api.acme.com", sslStatus: "pending", dnsVerified: false },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Custom Domains</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Custom domain mapping with SSL</p>

      <div className="mt-4 space-y-2">
        {domains.map((d) => (
          <div key={d.domain} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className={`h-2 w-2 rounded-full ${d.dnsVerified ? "bg-green-500" : "bg-zinc-300"}`} />
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{d.domain}</span>
            </div>
            <span className={`text-xs font-medium ${SSL_COLOR[d.sslStatus] ?? "text-zinc-500"}`}>
              {d.sslStatus}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {domains.filter((d) => d.sslStatus === "active").length}/{domains.length} SSL active
      </div>
    </div>
  );
}
