"use client";

import { useState } from "react";

interface ExtensionVersion {
  version: string;
  publishedAt: string;
  status: "latest" | "stable" | "beta" | "deprecated";
  changelog: string;
  size: string;
}

export function ExtensionVersionSelector({
  versions,
  currentVersion,
  onSelect,
  onInstall,
}: {
  versions: ExtensionVersion[];
  currentVersion?: string;
  onSelect?: (version: string) => void;
  onInstall?: (version: string) => void;
}) {
  const [selected, setSelected] = useState(currentVersion || versions[0]?.version || "");
  const [showChangelog, setShowChangelog] = useState(false);

  const selectedVersion = versions.find((v) => v.version === selected);

  const statusBadge: Record<string, { color: string; label: string }> = {
    latest: { color: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300", label: "Latest" },
    stable: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300", label: "Stable" },
    beta: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300", label: "Beta" },
    deprecated: { color: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300", label: "Deprecated" },
  };

  return (
    <div className="rounded-xl border dark:border-gray-700 p-4 space-y-3 max-w-sm">
      <h3 className="font-bold text-sm">📦 Select Version</h3>

      <div className="space-y-1 max-h-48 overflow-y-auto">
        {versions.map((v) => {
          const badge = statusBadge[v.status];
          const isCurrent = v.version === currentVersion;
          const isSelected = v.version === selected;
          return (
            <button key={v.version}
              onClick={() => { setSelected(v.version); onSelect?.(v.version); }}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm flex items-center justify-between ${
                isSelected ? "bg-blue-50 dark:bg-blue-900/10 border border-blue-500" : "hover:bg-gray-50 dark:hover:bg-gray-800"
              }`}>
              <div className="flex items-center gap-2">
                <span className="font-mono font-bold">v{v.version}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded-full ${badge.color}`}>{badge.label}</span>
                {isCurrent && <span className="text-xs text-green-500">✓ installed</span>}
              </div>
              <div className="text-xs text-gray-400">{v.publishedAt}</div>
            </button>
          );
        })}
      </div>

      {selectedVersion && (
        <div className="space-y-2">
          <div className="text-xs text-gray-500 flex justify-between">
            <span>Size: {selectedVersion.size}</span>
            <button onClick={() => setShowChangelog(!showChangelog)}
              className="text-blue-500 hover:underline">
              {showChangelog ? "Hide" : "Show"} changelog
            </button>
          </div>

          {showChangelog && (
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-xs text-gray-600 dark:text-gray-300 whitespace-pre-wrap">
              {selectedVersion.changelog}
            </div>
          )}

          <button onClick={() => onInstall?.(selected)}
            disabled={selected === currentVersion || selectedVersion.status === "deprecated"}
            className="w-full rounded-lg bg-blue-600 text-white py-2 text-sm font-medium disabled:opacity-50">
            {selected === currentVersion ? "✓ Currently Installed" : `Install v${selected}`}
          </button>
        </div>
      )}
    </div>
  );
}
