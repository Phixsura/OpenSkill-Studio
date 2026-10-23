"use client";

import { useState } from "react";

interface SdkInfo { language: string; latest: string; install: string; }
interface SdkInstallCardProps { sdks: SdkInfo[]; }

const langIcons: Record<string, string> = {
  typescript: "📘", python: "🐍", go: "🐹", ruby: "💎",
};

export function SdkInstallCard({ sdks }: SdkInstallCardProps) {
  const [selected, setSelected] = useState(sdks[0]?.language ?? "");
  const sdk = sdks.find(s => s.language === selected);
  const [copied, setCopied] = useState(false);

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">Install SDK</h3>
      <div className="flex gap-1">
        {sdks.map(s => (
          <button key={s.language} onClick={() => setSelected(s.language)}
            className={`rounded px-3 py-1 text-xs capitalize ${selected === s.language ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>
            {langIcons[s.language] ?? "📄"} {s.language}
          </button>
        ))}
      </div>
      {sdk && (
        <div className="rounded-lg bg-gray-950 p-3">
          <div className="flex items-center justify-between">
            <code className="text-sm text-green-400">{sdk.install}</code>
            <button onClick={() => { navigator.clipboard?.writeText(sdk.install); setCopied(true); setTimeout(() => setCopied(false), 2000); }}
              className="text-xs text-gray-400">{copied ? "✓" : "📋"}</button>
          </div>
          <p className="mt-1 text-xs text-gray-500">v{sdk.latest}</p>
        </div>
      )}
    </div>
  );
}
