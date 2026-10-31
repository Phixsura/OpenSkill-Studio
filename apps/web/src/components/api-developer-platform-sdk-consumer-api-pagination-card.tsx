"use client";

import { useState } from "react";

export default function PaginationCard() {
  const [config] = useState({ strategy: "cursor", defaultSize: 20, maxSize: 100 });
  const [example] = useState({ returned: 20, hasMore: true, totalItems: 1250 });

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Pagination Helper</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Cursor/offset pagination with metadata</p>

      <div className="mt-4 grid grid-cols-3 gap-3 text-center">
        <div className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-800">
          <div className="text-sm font-bold text-zinc-900 dark:text-zinc-100">{config.strategy}</div>
          <div className="text-xs text-zinc-500">Strategy</div>
        </div>
        <div className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-800">
          <div className="text-sm font-bold text-zinc-900 dark:text-zinc-100">{config.defaultSize}</div>
          <div className="text-xs text-zinc-500">Default Size</div>
        </div>
        <div className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-800">
          <div className="text-sm font-bold text-zinc-900 dark:text-zinc-100">{config.maxSize}</div>
          <div className="text-xs text-zinc-500">Max Size</div>
        </div>
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {example.returned} returned · {example.totalItems.toLocaleString()} total · has_more: {String(example.hasMore)}
      </div>
    </div>
  );
}
