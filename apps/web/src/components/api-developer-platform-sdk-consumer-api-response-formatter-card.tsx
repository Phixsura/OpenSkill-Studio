"use client";

import { useState } from "react";

export default function ResponseFormatterCard() {
  const [config] = useState({ defaultFormat: "json", envelope: true, meta: true, pretty: false });
  const [stats] = useState({ json: 12500, csv: 890, xml: 120, yaml: 45 });

  const total = Object.values(stats).reduce((s, v) => s + v, 0);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Response Formatter</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Format normalization with content negotiation</p>

      <div className="mt-4 grid grid-cols-4 gap-2 text-center">
        {Object.entries(stats).map(([fmt, count]) => (
          <div key={fmt} className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-800">
            <div className="text-sm font-bold text-zinc-900 dark:text-zinc-100">{count.toLocaleString()}</div>
            <div className="text-xs text-zinc-500">{fmt}</div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        Default: {config.defaultFormat} · {total.toLocaleString()} total formatted
      </div>
    </div>
  );
}
