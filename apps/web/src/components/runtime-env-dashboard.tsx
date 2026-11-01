"use client";

import { useState } from "react";

interface ResourceLimits {
  cpu: number;
  memoryMb: number;
  diskMb: number;
  networkEnabled: boolean;
}

interface RuntimeEnv {
  id: string;
  extensionId: string;
  runtime: string;
  state: "created" | "running" | "stopped" | "destroyed" | "error";
  limits: ResourceLimits;
  entrypoint: string;
  uptimeSeconds: number;
  startedAt?: string;
}

const stateConfig: Record<string, { color: string; icon: string }> = {
  created: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300", icon: "🆕" },
  running: { color: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300", icon: "🟢" },
  stopped: { color: "bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-300", icon: "🔴" },
  destroyed: { color: "bg-gray-200 text-gray-500 dark:bg-gray-800 dark:text-gray-500", icon: "💀" },
  error: { color: "bg-red-200 text-red-800 dark:bg-red-900/40 dark:text-red-300", icon: "⚠️" },
};

function formatUptime(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
  return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
}

export function RuntimeEnvDashboard({
  environments,
  onStart,
  onStop,
  onDestroy,
}: {
  environments: RuntimeEnv[];
  onStart?: (id: string) => void;
  onStop?: (id: string) => void;
  onDestroy?: (id: string) => void;
}) {
  const running = environments.filter((e) => e.state === "running").length;
  const total = environments.length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🖥️ Runtime Environments</h2>
        <span className="text-sm text-gray-500">{running}/{total} running</span>
      </div>

      <div className="grid gap-3">
        {environments.map((env) => {
          const cfg = stateConfig[env.state] || stateConfig.error;
          return (
            <div key={env.id} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span>{cfg.icon}</span>
                  <span className="font-mono text-sm font-semibold">{env.runtime}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{env.state}</span>
                </div>
                <div className="flex gap-1">
                  {(env.state === "created" || env.state === "stopped") && (
                    <button onClick={() => onStart?.(env.id)}
                      className="text-xs bg-green-600 text-white px-2 py-1 rounded">Start</button>
                  )}
                  {env.state === "running" && (
                    <button onClick={() => onStop?.(env.id)}
                      className="text-xs bg-yellow-600 text-white px-2 py-1 rounded">Stop</button>
                  )}
                  {env.state !== "destroyed" && (
                    <button onClick={() => onDestroy?.(env.id)}
                      className="text-xs bg-red-600 text-white px-2 py-1 rounded">Destroy</button>
                  )}
                </div>
              </div>
              <div className="grid grid-cols-4 gap-2 text-xs text-gray-500">
                <div><span className="block text-gray-400">CPU</span>{env.limits.cpu} cores</div>
                <div><span className="block text-gray-400">Memory</span>{env.limits.memoryMb} MB</div>
                <div><span className="block text-gray-400">Disk</span>{env.limits.diskMb} MB</div>
                <div><span className="block text-gray-400">Uptime</span>{env.state === "running" ? formatUptime(env.uptimeSeconds) : "—"}</div>
              </div>
              <div className="mt-1 text-xs text-gray-400">
                Entry: <code>{env.entrypoint}</code>
                {env.limits.networkEnabled && <span className="ml-2 text-blue-500">🌐 Network</span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
