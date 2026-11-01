"use client";

import { useState } from "react";

interface Capability {
  name: string;
  version: string;
  description: string;
}

interface ExtensionCaps {
  extensionId: string;
  provides: Capability[];
  requires: string[];
  requirementsMet: boolean;
  missingRequirements: string[];
}

export function CapabilityRegistryPanel({
  extensions,
  allCapabilities,
  onSearch,
}: {
  extensions: ExtensionCaps[];
  allCapabilities: string[];
  onSearch?: (capability: string) => void;
}) {
  const [search, setSearch] = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);

  const filtered = search
    ? extensions.filter((e) => e.provides.some((c) => c.name.includes(search)))
    : extensions;

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🧩 Capability Registry</h2>

      <div className="flex gap-2">
        <input type="text" value={search} onChange={(e) => { setSearch(e.target.value); onSearch?.(e.target.value); }}
          placeholder="Search capabilities..."
          className="flex-1 rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm" />
      </div>

      <div className="flex flex-wrap gap-1 text-xs">
        {allCapabilities.map((cap) => (
          <button key={cap} onClick={() => setSearch(cap)}
            className={`px-2 py-0.5 rounded-full ${search === cap ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {cap}
          </button>
        ))}
      </div>

      <div className="space-y-2">
        {filtered.map((ext) => (
          <div key={ext.extensionId} className="rounded-xl border dark:border-gray-700 overflow-hidden">
            <div className="flex items-center justify-between p-3 cursor-pointer"
              onClick={() => setExpanded(expanded === ext.extensionId ? null : ext.extensionId)}>
              <div className="flex items-center gap-2">
                <code className="text-sm font-semibold">{ext.extensionId}</code>
                <span className="text-xs text-gray-400">{ext.provides.length} capabilities</span>
                {!ext.requirementsMet && (
                  <span className="text-xs text-red-500">⚠ {ext.missingRequirements.length} missing</span>
                )}
              </div>
              <span className={`text-xs font-bold ${ext.requirementsMet ? "text-green-600" : "text-red-600"}`}>
                {ext.requirementsMet ? "✅" : "❌"}
              </span>
            </div>

            {expanded === ext.extensionId && (
              <div className="border-t dark:border-gray-700 p-3 bg-gray-50 dark:bg-gray-900/50 space-y-2">
                <div>
                  <span className="text-xs font-semibold text-gray-500">Provides</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {ext.provides.map((c) => (
                      <span key={c.name} className="text-xs bg-green-100 dark:bg-green-900/30 text-green-700 px-2 py-0.5 rounded-full">
                        {c.name} v{c.version}
                      </span>
                    ))}
                  </div>
                </div>
                {ext.requires.length > 0 && (
                  <div>
                    <span className="text-xs font-semibold text-gray-500">Requires</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {ext.requires.map((r) => (
                        <span key={r} className={`text-xs px-2 py-0.5 rounded-full ${
                          ext.missingRequirements.includes(r) ? "bg-red-100 text-red-600" : "bg-blue-100 text-blue-700"
                        }`}>{r}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
