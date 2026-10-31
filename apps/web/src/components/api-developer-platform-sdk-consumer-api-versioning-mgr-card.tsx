"use client";

import { useState } from "react";

interface ApiVer {
  version: string;
  status: "active" | "deprecated" | "sunset";
  releaseDate: string;
}

const STATUS_STYLE: Record<string, string> = {
  active: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  deprecated: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
  sunset: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function VersioningManagerCard() {
  const [versions] = useState<ApiVer[]>([
    { version: "3.0.0", status: "active", releaseDate: "2024-10-01" },
    { version: "2.1.0", status: "deprecated", releaseDate: "2024-06-15" },
    { version: "1.0.0", status: "sunset", releaseDate: "2023-01-01" },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        API Versioning
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Semantic versioning with deprecation lifecycle
      </p>

      <div className="mt-4 space-y-2">
        {versions.map((v) => (
          <div
            key={v.version}
            className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700"
          >
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                v{v.version}
              </span>
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_STYLE[v.status]}`}>
                {v.status}
              </span>
            </div>
            <span className="text-xs text-zinc-400">{v.releaseDate}</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {versions.filter((v) => v.status === "active").length} active version{versions.filter((v) => v.status === "active").length !== 1 ? "s" : ""}
      </div>
    </div>
  );
}
