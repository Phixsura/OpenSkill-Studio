"use client";

import { useState } from "react";

interface Environment { environment: string; currentVersion: string | null; deployed: boolean; icon: string; }
interface DeployPageProps { appName: string; environments: Environment[];
  availableVersions: string[]; onDeploy: (version: string, env: string) => void; }

export function DeployPage({ appName, environments, availableVersions, onDeploy }: DeployPageProps) {
  const [version, setVersion] = useState(availableVersions[0] ?? "");
  const [env, setEnv] = useState("staging");

  return (
    <div className="space-y-5">
      <h2 className="text-lg font-bold">🚀 Deploy {appName}</h2>
      <div className="grid grid-cols-3 gap-3">
        {environments.map(e => (
          <div key={e.environment} className={`rounded-xl border p-4 text-center ${e.deployed ? "dark:border-gray-700" : "border-dashed dark:border-gray-600"}`}>
            <span className="text-2xl">{e.icon}</span>
            <p className="text-sm font-semibold capitalize mt-1">{e.environment}</p>
            <p className="text-xs text-gray-400">{e.currentVersion ? `v${e.currentVersion}` : "Not deployed"}</p>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs text-gray-400 mb-1">Version</label>
          <select value={version} onChange={e => setVersion(e.target.value)}
            className="w-full rounded border px-3 py-2 text-sm font-mono dark:bg-gray-800 dark:border-gray-600">
            {availableVersions.map(v => <option key={v}>{v}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs text-gray-400 mb-1">Environment</label>
          <select value={env} onChange={e => setEnv(e.target.value)}
            className="w-full rounded border px-3 py-2 text-sm capitalize dark:bg-gray-800 dark:border-gray-600">
            {environments.map(e => <option key={e.environment} value={e.environment}>{e.environment}</option>)}
          </select>
        </div>
      </div>
      <button onClick={() => onDeploy(version, env)}
        className="w-full rounded-lg bg-green-600 py-3 text-sm font-medium text-white">🚀 Deploy v{version} to {env}</button>
    </div>
  );
}
