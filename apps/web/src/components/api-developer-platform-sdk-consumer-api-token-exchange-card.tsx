"use client";

import { useState } from "react";

export default function TokenExchangeCard() {
  const [stats] = useState({
    registeredTokens: 24,
    issuedExchanges: 1580,
    trustedAudiences: 5,
  });
  const [audiences] = useState(["auth-service", "billing-service", "analytics-service"]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Token Exchange</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Cross-service token exchange</p>

      <div className="mt-4 grid grid-cols-3 gap-3 text-center">
        <div className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-800">
          <div className="text-lg font-bold text-zinc-900 dark:text-zinc-100">{stats.registeredTokens}</div>
          <div className="text-xs text-zinc-500">Tokens</div>
        </div>
        <div className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-800">
          <div className="text-lg font-bold text-zinc-900 dark:text-zinc-100">{stats.issuedExchanges.toLocaleString()}</div>
          <div className="text-xs text-zinc-500">Exchanges</div>
        </div>
        <div className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-800">
          <div className="text-lg font-bold text-zinc-900 dark:text-zinc-100">{stats.trustedAudiences}</div>
          <div className="text-xs text-zinc-500">Audiences</div>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap gap-1">
        {audiences.map((a) => (
          <span key={a} className="rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-700 dark:bg-blue-900 dark:text-blue-300">{a}</span>
        ))}
      </div>
    </div>
  );
}
