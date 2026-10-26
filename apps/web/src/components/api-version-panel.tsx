"use client";

import { useState } from "react";

interface ApiVersionInfo {
  version: string;
  status: "active" | "deprecated" | "sunset" | "beta";
  endpoints: number;
  requests: number;
  isDefault: boolean;
  sunsetDate?: string;
}

const statusConfig: Record<string, { color: string; icon: string }> = {
  active: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "🟢" },
  beta: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30", icon: "🔵" },
  deprecated: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "⚠️" },
  sunset: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "🌅" },
};

export function ApiVersionPanel({
  versions,
  onSetDefault,
  onDeprecate,
}: {
  versions: ApiVersionInfo[];
  onSetDefault?: (version: string) => void;
  onDeprecate?: (version: string) => void;
}) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📌 API Versions</h2>

      <div className="space-y-2">
        {versions.map((v) => {
          const cfg = statusConfig[v.status];
          return (
            <div key={v.version}
              className={`rounded-xl border-2 p-4 ${v.isDefault ? "border-blue-500" : "dark:border-gray-700 border-gray-200"}`}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span>{cfg.icon}</span>
                  <span className="font-bold text-lg">{v.version}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{v.status}</span>
                  {v.isDefault && <span className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded-full">default</span>}
                </div>
                <div className="flex gap-1">
                  {!v.isDefault && v.status === "active" && (
                    <button onClick={() => onSetDefault?.(v.version)}
                      className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Set Default</button>
                  )}
                  {v.status === "active" && (
                    <button onClick={() => onDeprecate?.(v.version)}
                      className="text-xs bg-yellow-600 text-white px-2 py-1 rounded">Deprecate</button>
                  )}
                </div>
              </div>
              <div className="flex gap-4 text-xs text-gray-500">
                <span>{v.endpoints} endpoints</span>
                <span>{v.requests.toLocaleString()} requests</span>
                {v.sunsetDate && <span className="text-red-500">Sunset: {v.sunsetDate}</span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
