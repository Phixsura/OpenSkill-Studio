"use client";

import { useState } from "react";

interface DocEntry {
  method: string;
  path: string;
  summary: string;
  deprecated: boolean;
}

const METHOD_COLOR: Record<string, string> = {
  GET: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  POST: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  PUT: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300",
  DELETE: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function DocGeneratorCard() {
  const [docs] = useState<DocEntry[]>([
    { method: "GET", path: "/api/users", summary: "List all users", deprecated: false },
    { method: "POST", path: "/api/users", summary: "Create a user", deprecated: false },
    { method: "GET", path: "/api/v1/legacy", summary: "Legacy endpoint", deprecated: true },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Doc Generator
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Auto-generate docs from endpoint metadata
      </p>

      <div className="mt-4 space-y-2">
        {docs.map((d) => (
          <div key={`${d.method}:${d.path}`} className={`flex items-center gap-2 rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700 ${d.deprecated ? "opacity-50" : ""}`}>
            <span className={`rounded px-1.5 py-0.5 text-xs font-bold ${METHOD_COLOR[d.method] ?? ""}`}>{d.method}</span>
            <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{d.path}</span>
            <span className="ml-auto text-xs text-zinc-400">{d.summary}</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {docs.filter((d) => !d.deprecated).length} active · {docs.filter((d) => d.deprecated).length} deprecated
      </div>
    </div>
  );
}
