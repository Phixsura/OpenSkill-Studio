"use client";

import { useState } from "react";

interface ChangelogEntry {
  version: string;
  date: string;
  changes: { type: "added" | "fixed" | "changed" | "removed"; description: string }[];
  yanked?: boolean;
}

export function ExtensionChangelogViewer({
  extensionName,
  entries,
}: {
  extensionName: string;
  entries: ChangelogEntry[];
}) {
  const [expandedVersion, setExpandedVersion] = useState<string | null>(
    entries[0]?.version || null
  );

  const typeConfig = {
    added: { label: "Added", color: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300", icon: "✨" },
    fixed: { label: "Fixed", color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300", icon: "🐛" },
    changed: { label: "Changed", color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300", icon: "🔄" },
    removed: { label: "Removed", color: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300", icon: "🗑️" },
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📜 {extensionName} Changelog</h2>

      <div className="space-y-2">
        {entries.map((entry) => {
          const isExpanded = expandedVersion === entry.version;
          return (
            <div
              key={entry.version}
              className={`rounded-xl border dark:border-gray-700 overflow-hidden ${
                entry.yanked ? "opacity-60" : ""
              }`}
            >
              <button
                onClick={() => setExpandedVersion(isExpanded ? null : entry.version)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-800/50"
              >
                <div className="flex items-center gap-3">
                  <span className="font-mono font-bold text-blue-600 dark:text-blue-400">
                    v{entry.version}
                  </span>
                  <span className="text-sm text-gray-500">{entry.date}</span>
                  {entry.yanked && (
                    <span className="text-xs bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-300 px-2 py-0.5 rounded">
                      Yanked
                    </span>
                  )}
                  <span className="text-xs text-gray-400">
                    {entry.changes.length} change{entry.changes.length !== 1 ? "s" : ""}
                  </span>
                </div>
                <span className="text-gray-400">{isExpanded ? "▼" : "▶"}</span>
              </button>

              {isExpanded && (
                <div className="px-4 pb-4 space-y-2">
                  {entry.changes.map((change, i) => {
                    const cfg = typeConfig[change.type];
                    return (
                      <div key={i} className="flex items-start gap-2 text-sm">
                        <span className={`shrink-0 text-xs px-2 py-0.5 rounded-full ${cfg.color}`}>
                          {cfg.icon} {cfg.label}
                        </span>
                        <span>{change.description}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
