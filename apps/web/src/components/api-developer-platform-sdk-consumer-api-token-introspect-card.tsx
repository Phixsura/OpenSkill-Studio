"use client";

import { useState } from "react";

interface TokenRow {
  tokenId: string;
  type: string;
  active: boolean;
  remainingHrs: number | null;
}

export default function TokenIntrospectCard() {
  const [tokens] = useState<TokenRow[]>([
    { tokenId: "tok_a1b2c3", type: "access", active: true, remainingHrs: 22 },
    { tokenId: "tok_d4e5f6", type: "refresh", active: true, remainingHrs: 168 },
    { tokenId: "tok_g7h8i9", type: "api_key", active: false, remainingHrs: null },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Token Introspection</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Token metadata inspection with expiry checks</p>

      <div className="mt-4 space-y-2">
        {tokens.map((t) => (
          <div key={t.tokenId} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className={`h-2 w-2 rounded-full ${t.active ? "bg-green-500" : "bg-red-500"}`} />
              <code className="text-sm text-zinc-800 dark:text-zinc-200">{t.tokenId}</code>
              <span className="rounded bg-zinc-100 px-1.5 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">{t.type}</span>
            </div>
            <span className="text-xs text-zinc-400">
              {t.remainingHrs !== null ? `${t.remainingHrs}h left` : "revoked"}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {tokens.filter((t) => t.active).length}/{tokens.length} tokens active
      </div>
    </div>
  );
}
