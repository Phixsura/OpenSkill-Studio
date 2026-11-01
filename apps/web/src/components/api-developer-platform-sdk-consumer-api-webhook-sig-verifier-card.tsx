"use client";

import { useState } from "react";

interface WebhookSig {
  webhookId: string;
  algorithm: string;
  lastVerified: string;
  status: "active" | "expired";
}

export default function WebhookSigVerifierCard() {
  const [sigs] = useState<WebhookSig[]>([
    { webhookId: "wh-orders", algorithm: "sha256", lastVerified: "2 min ago", status: "active" },
    { webhookId: "wh-payments", algorithm: "sha512", lastVerified: "1 hr ago", status: "active" },
    { webhookId: "wh-legacy", algorithm: "sha256", lastVerified: "3 days ago", status: "expired" },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Signature Verifier
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        HMAC signature verification with replay protection
      </p>

      <div className="mt-4 space-y-2">
        {sigs.map((s) => (
          <div
            key={s.webhookId}
            className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700"
          >
            <div>
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">
                {s.webhookId}
              </span>
              <span className="ml-2 rounded bg-zinc-100 px-1.5 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">
                {s.algorithm}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-zinc-400">{s.lastVerified}</span>
              <span
                className={`h-2 w-2 rounded-full ${s.status === "active" ? "bg-green-500" : "bg-red-500"}`}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {sigs.filter((s) => s.status === "active").length} active webhooks
      </div>
    </div>
  );
}
