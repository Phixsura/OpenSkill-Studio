"use client";

import { useState } from "react";

interface InstallSnippetCopyProps { commands: Record<string, string>; defaultManager: string;
  onCopy: (command: string) => void; }

const managerIcon: Record<string, string> = {
  npm: "📦", yarn: "🧶", pnpm: "⚡", pip: "🐍", uv: "🟣",
};

export function InstallSnippetCopy({ commands, defaultManager, onCopy }: InstallSnippetCopyProps) {
  const [manager, setManager] = useState(defaultManager);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    onCopy(commands[manager] ?? "");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-lg border dark:border-gray-700">
      <div className="flex border-b dark:border-gray-700">
        {Object.keys(commands).map(m => (
          <button key={m} onClick={() => setManager(m)}
            className={`px-3 py-1.5 text-xs ${manager === m ? "bg-gray-100 font-medium dark:bg-gray-800" : "text-gray-400"}`}>
            {managerIcon[m] ?? "📦"} {m}
          </button>
        ))}
      </div>
      <div className="flex items-center justify-between px-4 py-2.5">
        <code className="font-mono text-sm">{commands[manager]}</code>
        <button onClick={handleCopy}
          className="rounded border px-2.5 py-1 text-xs dark:border-gray-600">
          {copied ? "Copied! ✓" : "Copy"}
        </button>
      </div>
    </div>
  );
}
