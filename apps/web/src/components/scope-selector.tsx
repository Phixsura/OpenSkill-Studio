"use client";

import { useState } from "react";

const SCOPE_GROUPS = {
  read: ["read:cohorts", "read:projects", "read:submissions", "read:skills", "read:analytics", "read:talent", "read:packs", "read:workflows"],
  write: ["write:cohorts", "write:projects", "write:skills", "write:talent", "write:packs", "write:evaluations"],
  special: ["subscribe:events", "extend:ui", "run:background_jobs", "export:analytics"],
};

const SCOPE_ICONS: Record<string, string> = { read: "👁️", write: "✏️", special: "⚡" };

interface ScopeSelectorProps {
  selected: string[];
  onChange: (scopes: string[]) => void;
  maxScopes?: string[];
}

export function ScopeSelector({ selected, onChange, maxScopes }: ScopeSelectorProps) {
  const toggle = (scope: string) => {
    onChange(selected.includes(scope) ? selected.filter(s => s !== scope) : [...selected, scope]);
  };

  const available = (scope: string) => !maxScopes || maxScopes.includes(scope);

  return (
    <div className="space-y-4">
      {Object.entries(SCOPE_GROUPS).map(([group, scopes]) => (
        <div key={group}>
          <h4 className="mb-2 text-sm font-semibold capitalize">
            {SCOPE_ICONS[group]} {group}
          </h4>
          <div className="flex flex-wrap gap-2">
            {scopes.map(scope => (
              <button
                key={scope}
                onClick={() => available(scope) && toggle(scope)}
                disabled={!available(scope)}
                className={`rounded-full border px-3 py-1 text-xs transition-colors ${
                  selected.includes(scope)
                    ? "border-blue-500 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                    : "border-gray-300 text-gray-600 dark:border-gray-600 dark:text-gray-400"
                } ${!available(scope) ? "cursor-not-allowed opacity-40" : "cursor-pointer hover:border-blue-400"}`}
              >
                {scope}
              </button>
            ))}
          </div>
        </div>
      ))}
      <p className="text-xs text-gray-500">{selected.length} scope{selected.length !== 1 ? "s" : ""} selected</p>
    </div>
  );
}
