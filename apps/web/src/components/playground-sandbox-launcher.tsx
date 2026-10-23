"use client";

import { useState } from "react";

interface PlaygroundSandboxLauncherProps { appName: string; templates: string[];
  onLaunch: (template: string) => void; activeSandboxes: number; maxConcurrent: number; }

const templateIcons: Record<string, string> = {
  default: "📦", react: "⚛️", node: "🟢", python: "🐍", fullstack: "🏗️",
};

export function PlaygroundSandboxLauncher({ appName, templates, onLaunch, activeSandboxes, maxConcurrent }: PlaygroundSandboxLauncherProps) {
  const [selected, setSelected] = useState(templates[0] ?? "default");
  const canLaunch = activeSandboxes < maxConcurrent;
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold">Try {appName}</h2>
        <p className="text-sm text-gray-400">{activeSandboxes}/{maxConcurrent} sandboxes active</p>
      </div>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {templates.map(t => (
          <button key={t} onClick={() => setSelected(t)}
            className={`rounded-lg border p-3 text-center ${selected === t ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "dark:border-gray-700"}`}>
            <span className="text-2xl">{templateIcons[t] ?? "📦"}</span>
            <p className="mt-1 text-sm capitalize">{t}</p>
          </button>
        ))}
      </div>
      <button onClick={() => onLaunch(selected)} disabled={!canLaunch}
        className="w-full rounded-lg bg-green-600 py-2.5 text-sm font-semibold text-white disabled:opacity-50">
        {canLaunch ? `Launch ${selected} Sandbox` : "Max sandboxes reached"}
      </button>
    </div>
  );
}
