"use client";

import { useState } from "react";

interface CorsInfo {
  consumerId: string;
  origins: string[];
  methods: string[];
  credentials: boolean;
}

export default function CorsPolicyCard() {
  const [policy] = useState<CorsInfo>({
    consumerId: "c-acme",
    origins: ["https://app.acme.com", "https://staging.acme.com", "http://localhost:3000"],
    methods: ["GET", "POST", "PUT", "DELETE"],
    credentials: true,
  });

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">CORS Policy</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Per-consumer CORS configuration</p>

      <div className="mt-4">
        <div className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Allowed Origins</div>
        <div className="mt-1 space-y-1">
          {policy.origins.map((o) => (
            <div key={o} className="rounded bg-zinc-50 px-2 py-1 font-mono text-xs text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">{o}</div>
          ))}
        </div>
      </div>

      <div className="mt-3 flex flex-wrap gap-1">
        {policy.methods.map((m) => (
          <span key={m} className="rounded bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900 dark:text-blue-300">{m}</span>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        Credentials: {policy.credentials ? "enabled" : "disabled"} · {policy.origins.length} origins
      </div>
    </div>
  );
}
