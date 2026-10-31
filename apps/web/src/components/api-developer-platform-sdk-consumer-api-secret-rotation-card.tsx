"use client";

import { useState } from "react";

interface VersionInfo {
  version: number;
  status: "active" | "grace" | "expired";
  prefix: string;
}

export default function SecretRotationCard() {
  const [versions] = useState<VersionInfo[]>([
    { version: 3, status: "active", prefix: "sk_3f8a..." },
    { version: 2, status: "grace", prefix: "sk_9b2c..." },
    { version: 1, status: "expired", prefix: "sk_1a0d..." },
  ]);

  const STATUS_STYLE: Record<string, string> = {
    active: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
    grace: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300",
    expired: "bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400",
  };

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Secret Rotation
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Automated secret rotation with grace period
      </p>

      <div className="mt-4 space-y-2">
        {versions.map((v) => (
          <div key={v.version} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">v{v.version}</span>
              <span className="font-mono text-xs text-zinc-400">{v.prefix}</span>
            </div>
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_STYLE[v.status]}`}>{v.status}</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {versions.filter((v) => v.status !== "expired").length} valid versions
      </div>
    </div>
  );
}
