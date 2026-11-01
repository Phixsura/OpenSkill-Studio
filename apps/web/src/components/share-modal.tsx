"use client";

import { useState } from "react";

interface Platform { id: string; label: string; icon: string; url: string; }
interface ShareModalProps { appName: string; platforms: Platform[]; copyUrl: string;
  embedCode: string; onClose: () => void; }

export function ShareModal({ appName, platforms, copyUrl, embedCode, onClose }: ShareModalProps) {
  const [copied, setCopied] = useState(false);
  const [tab, setTab] = useState<"share" | "embed">("share");
  const handleCopy = (text: string) => { navigator.clipboard?.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000); };

  return (
    <div className="mx-auto max-w-md rounded-xl border bg-white p-5 shadow-xl dark:border-gray-700 dark:bg-gray-900">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Share {appName}</h2>
        <button onClick={onClose} className="text-gray-400">✕</button>
      </div>
      <div className="mt-3 flex gap-1">
        {(["share", "embed"] as const).map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`rounded px-3 py-1 text-xs capitalize ${tab === t ? "bg-blue-600 text-white" : "border dark:border-gray-600"}`}>{t}</button>
        ))}
      </div>
      {tab === "share" ? (
        <div className="mt-4 space-y-3">
          <div className="grid grid-cols-3 gap-2">
            {platforms.map(p => (
              <a key={p.id} href={p.url} target="_blank" rel="noopener noreferrer"
                className="flex flex-col items-center gap-1 rounded-lg border p-3 text-center hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
                <span className="text-xl">{p.icon}</span>
                <span className="text-xs">{p.label}</span>
              </a>
            ))}
          </div>
          <div className="flex gap-2">
            <input value={copyUrl} readOnly className="flex-1 rounded border px-3 py-1.5 text-xs dark:border-gray-600 dark:bg-gray-700" />
            <button onClick={() => handleCopy(copyUrl)} className="rounded bg-blue-600 px-3 py-1.5 text-xs text-white">
              {copied ? "Copied!" : "Copy"}
            </button>
          </div>
        </div>
      ) : (
        <div className="mt-4">
          <div className="rounded bg-gray-900 p-3 font-mono text-xs text-green-400">{embedCode}</div>
          <button onClick={() => handleCopy(embedCode)} className="mt-2 w-full rounded border py-1.5 text-xs dark:border-gray-600">
            Copy Embed Code
          </button>
        </div>
      )}
    </div>
  );
}
