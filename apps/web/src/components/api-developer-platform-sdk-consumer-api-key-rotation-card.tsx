"use client";

import { useState } from "react";

interface KeyInfo { keyId: string; version: number; status: string; intervalDays: number; autoRotate: boolean; }

export default function KeyRotationCard() {
  const [keys] = useState<KeyInfo[]>([
    { keyId: "key_a1b2c3", version: 5, status: "active", intervalDays: 30, autoRotate: true },
    { keyId: "key_d4e5f6", version: 2, status: "active", intervalDays: 90, autoRotate: true },
    { keyId: "key_g7h8i9", version: 1, status: "revoked", intervalDays: 90, autoRotate: false },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Key Rotation</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Automated API key rotation scheduling</p>

      <div className="mt-4 space-y-2">
        {keys.map((k) => (
          <div key={k.keyId} className={`flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700 ${k.status === "revoked" ? "opacity-50" : ""}`}>
            <div className="flex items-center gap-2">
              <code className="text-sm text-zinc-800 dark:text-zinc-200">{k.keyId}</code>
              <span className="text-xs text-zinc-400">v{k.version}</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="text-zinc-500">{k.intervalDays}d</span>
              <span className={k.autoRotate ? "text-green-600 dark:text-green-400" : "text-zinc-400"}>
                {k.autoRotate ? "auto" : "manual"}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {keys.filter((k) => k.status === "active").length} active keys
      </div>
    </div>
  );
}
