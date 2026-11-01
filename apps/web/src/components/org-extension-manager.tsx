"use client";

import { useState } from "react";

interface OrgExtension {
  id: string;
  name: string;
  icon: string;
  version: string;
  status: "enabled" | "disabled" | "updating" | "error";
  installedAt: string;
  lastUsed: string;
  usagePercent: number;
}

export function OrgExtensionManager({
  extensions,
  orgName,
  onEnable,
  onDisable,
  onUninstall,
  onUpdate,
}: {
  extensions: OrgExtension[];
  orgName: string;
  onEnable?: (id: string) => void;
  onDisable?: (id: string) => void;
  onUninstall?: (id: string) => void;
  onUpdate?: (id: string) => void;
}) {
  const [filter, setFilter] = useState<string>("all");

  const filtered = filter === "all" ? extensions : extensions.filter((e) => e.status === filter);

  const statusConfig: Record<string, { dot: string; label: string }> = {
    enabled: { dot: "bg-green-500", label: "Enabled" },
    disabled: { dot: "bg-gray-400", label: "Disabled" },
    updating: { dot: "bg-blue-500 animate-pulse", label: "Updating" },
    error: { dot: "bg-red-500", label: "Error" },
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📦 {orgName} Extensions</h2>
        <div className="flex gap-1">
          {["all", "enabled", "disabled", "error"].map((f) => (
            <button key={f} onClick={() => setFilter(f)}
              className={`text-xs px-2.5 py-1 rounded-full ${
                filter === f ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"
              }`}>{f}</button>
          ))}
        </div>
      </div>

      <div className="text-sm text-gray-500">{filtered.length} extension{filtered.length !== 1 ? "s" : ""}</div>

      <div className="space-y-2">
        {filtered.map((ext) => {
          const cfg = statusConfig[ext.status];
          return (
            <div key={ext.id} className="rounded-xl border dark:border-gray-700 p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{ext.icon}</span>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm">{ext.name}</span>
                    <span className="text-xs text-gray-400 font-mono">v{ext.version}</span>
                    <div className="flex items-center gap-1">
                      <div className={`w-2 h-2 rounded-full ${cfg.dot}`} />
                      <span className="text-xs text-gray-500">{cfg.label}</span>
                    </div>
                  </div>
                  <div className="text-xs text-gray-400 mt-0.5">
                    Installed: {ext.installedAt} · Last used: {ext.lastUsed} · Usage: {ext.usagePercent}%
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                {ext.status === "enabled" && onDisable && (
                  <button onClick={() => onDisable(ext.id)} className="text-xs text-yellow-500 border border-yellow-300 dark:border-yellow-700 px-2 py-1 rounded">Disable</button>
                )}
                {ext.status === "disabled" && onEnable && (
                  <button onClick={() => onEnable(ext.id)} className="text-xs text-green-500 border border-green-300 dark:border-green-700 px-2 py-1 rounded">Enable</button>
                )}
                {onUpdate && ext.status !== "updating" && (
                  <button onClick={() => onUpdate(ext.id)} className="text-xs text-blue-500 border border-blue-300 dark:border-blue-700 px-2 py-1 rounded">Update</button>
                )}
                {onUninstall && (
                  <button onClick={() => onUninstall(ext.id)} className="text-xs text-red-500 border border-red-300 dark:border-red-700 px-2 py-1 rounded">Uninstall</button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
