"use client";

import { useState } from "react";

interface IpEntry {
  network: string;
  label: string;
}

export default function IpAllowlistCard() {
  const [entries] = useState<IpEntry[]>([
    { network: "10.0.0.0/24", label: "Office" },
    { network: "192.168.1.0/24", label: "VPN" },
    { network: "203.0.113.50/32", label: "CI Server" },
  ]);
  const [mode] = useState<"allow" | "deny">("allow");

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
          IP Allowlist
        </h3>
        <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900 dark:text-blue-300">
          {mode} mode
        </span>
      </div>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        IP-based access control with CIDR support
      </p>

      <div className="mt-4 space-y-2">
        {entries.map((e) => (
          <div
            key={e.network}
            className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700"
          >
            <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">
              {e.network}
            </span>
            <span className="text-xs text-zinc-500 dark:text-zinc-400">{e.label}</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {entries.length} entries configured
      </div>
    </div>
  );
}
