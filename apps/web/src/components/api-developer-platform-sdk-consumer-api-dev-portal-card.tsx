"use client";

import { useState } from "react";

export default function DevPortalCard() {
  const [portal] = useState({
    steps: ["Create Account", "Generate API Key", "Make First Call", "Set Up Webhooks"],
    sections: 24,
    quicklinks: [
      { title: "API Docs", icon: "📖" },
      { title: "Status Page", icon: "🟢" },
      { title: "Support", icon: "💬" },
    ],
  });

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Developer Portal</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Unified portal with getting started guide</p>

      <div className="mt-4">
        <div className="text-xs font-medium text-zinc-500 dark:text-zinc-400 mb-2">Getting Started</div>
        <div className="space-y-1">
          {portal.steps.map((step, i) => (
            <div key={step} className="flex items-center gap-2 text-sm">
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700 dark:bg-blue-900 dark:text-blue-300">{i + 1}</span>
              <span className="text-zinc-800 dark:text-zinc-200">{step}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-3 flex gap-2">
        {portal.quicklinks.map((q) => (
          <span key={q.title} className="rounded bg-zinc-100 px-2 py-1 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">{q.icon} {q.title}</span>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">{portal.sections} documentation sections</div>
    </div>
  );
}
