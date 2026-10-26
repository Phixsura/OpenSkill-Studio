"use client";

import { useState } from "react";

interface ChangelogEntry {
  description: string;
  category: string;
  isBreaking: boolean;
}

interface Release {
  version: string;
  date: string;
  entries: ChangelogEntry[];
  yanked: boolean;
}

const categoryColors: Record<string, string> = {
  Added: "bg-green-100 text-green-700 dark:bg-green-900/30",
  Changed: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  Fixed: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  Removed: "bg-red-100 text-red-700 dark:bg-red-900/30",
  Deprecated: "bg-gray-100 text-gray-600 dark:bg-gray-800",
  Security: "bg-purple-100 text-purple-700 dark:bg-purple-900/30",
};

export function ChangelogTimeline({
  releases,
  extensionName,
}: {
  releases: Release[];
  extensionName: string;
}) {
  const [expanded, setExpanded] = useState<string | null>(releases[0]?.version || null);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📋 {extensionName} Changelog</h2>

      <div className="relative">
        <div className="absolute left-3 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700" />

        {releases.map((release) => {
          const isExpanded = expanded === release.version;
          const hasBreaking = release.entries.some((e) => e.isBreaking);

          return (
            <div key={release.version} className="relative pl-8 pb-4">
              <div className={`absolute left-1.5 w-3 h-3 rounded-full mt-1.5 ${
                release.yanked ? "bg-red-500" : hasBreaking ? "bg-yellow-500" : "bg-blue-500"
              }`} />

              <div className="cursor-pointer" onClick={() => setExpanded(isExpanded ? null : release.version)}>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-sm">v{release.version}</span>
                  {release.date && <span className="text-xs text-gray-400">{release.date}</span>}
                  {release.yanked && <span className="text-xs bg-red-600 text-white px-1.5 py-0.5 rounded">YANKED</span>}
                  {hasBreaking && <span className="text-xs text-yellow-600 font-medium">⚠ Breaking</span>}
                  <span className="text-xs text-gray-400">{release.entries.length} changes</span>
                </div>
              </div>

              {isExpanded && (
                <div className="mt-2 space-y-1">
                  {release.entries.map((entry, i) => (
                    <div key={i} className="flex items-start gap-2 text-sm">
                      <span className={`text-xs px-1.5 py-0.5 rounded shrink-0 ${categoryColors[entry.category] || "bg-gray-100"}`}>
                        {entry.category}
                      </span>
                      <span className={entry.isBreaking ? "font-semibold" : ""}>
                        {entry.description}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
