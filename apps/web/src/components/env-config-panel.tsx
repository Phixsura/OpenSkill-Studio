"use client";
import { useState } from "react";

const envOrder = ["development", "staging", "production"];
const envIcons: Record<string, string> = { development: "🔧", staging: "🧪", production: "🚀" };

export function EnvConfigPanel({ configs, activeEnv, onSwitch, onPromote }: {
  configs: Record<string, Record<string, string>>; activeEnv: string;
  onSwitch?: (env: string) => void; onPromote?: (from: string, to: string) => void;
}) {
  const current = configs[activeEnv] || {};
  const entries = Object.entries(current);
  return (
    <div className="space-y-3">
      <div className="flex gap-1">
        {envOrder.map(e => (
          <button key={e} onClick={() => onSwitch?.(e)}
            className={`text-xs px-3 py-1.5 rounded-full capitalize ${activeEnv === e ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>
            {envIcons[e]} {e}
          </button>
        ))}
      </div>
      {entries.length === 0 ? (
        <div className="text-center text-gray-400 py-4 text-sm">No config values</div>
      ) : (
        <div className="space-y-1">
          {entries.map(([k, v]) => (
            <div key={k} className="flex items-center justify-between border dark:border-gray-700 rounded-lg p-2 text-sm">
              <code className="text-xs font-mono font-bold">{k}</code>
              <code className="text-xs font-mono text-gray-500">{v}</code>
            </div>
          ))}
        </div>
      )}
      {activeEnv !== "production" && (
        <button onClick={() => onPromote?.(activeEnv, envOrder[envOrder.indexOf(activeEnv) + 1])}
          className="w-full text-xs bg-green-500 text-white py-1.5 rounded-lg">
          Promote to {envOrder[envOrder.indexOf(activeEnv) + 1]} →
        </button>
      )}
    </div>
  );
}
