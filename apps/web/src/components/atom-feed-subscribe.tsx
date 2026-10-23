"use client";
import { useState } from "react";

interface AtomFeedSubscribeProps { feedUrl: string; appName: string; itemCount: number; }

export function AtomFeedSubscribe({ feedUrl, appName, itemCount }: AtomFeedSubscribeProps) {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard?.writeText(feedUrl).then(() => { setCopied(true); setTimeout(() => setCopied(false), 2000); });
  };
  return (
    <div className="rounded-xl border p-4 dark:border-gray-700">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-lg">📡</span>
        <h4 className="text-sm font-semibold">Subscribe to {appName} Changelog</h4>
      </div>
      <p className="text-xs text-gray-400 mb-3">{itemCount} releases · Atom feed</p>
      <div className="flex gap-2">
        <input readOnly value={feedUrl} className="flex-1 text-xs font-mono px-2 py-1.5 border rounded bg-gray-50 dark:bg-gray-800 dark:border-gray-600" />
        <button onClick={handleCopy}
          className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700">
          {copied ? "✓" : "Copy"}
        </button>
      </div>
    </div>
  );
}
