"use client";

import { useState } from "react";

interface EnvInfo {
  env: string;
  varCount: number;
  secretCount: number;
  locked: boolean;
}

const ENV_COLOR: Record<string, string> = {
  development: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  staging: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300",
  production: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function EnvManagerCard() {
  const [envs] = useState<EnvInfo[]>([
    { env: "development", varCount: 12, secretCount: 3, locked: false },
    { env: "staging", varCount: 12, secretCount: 3, locked: false },
    { env: "production", varCount: 10, secretCount: 5, locked: true },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Environment Manager
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Multi-environment config with promotion
      </p>

      <div className="mt-4 space-y-2">
        {envs.map((e) => (
          <div key={e.env} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${ENV_COLOR[e.env] ?? ""}`}>{e.env}</span>
              {e.locked && <span className="text-xs text-zinc-400">🔒</span>}
            </div>
            <span className="text-xs text-zinc-500">{e.varCount} vars · {e.secretCount} secrets</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        dev → staging → production
      </div>
    </div>
  );
}
