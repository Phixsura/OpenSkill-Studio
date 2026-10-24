"use client";

import { useState } from "react";

interface DeepLinkGeneratorCardProps {
  deepLink: string; shortLink: string; webFallback: string; qrUrl: string;
}

export function DeepLinkGeneratorCard({ deepLink, shortLink, webFallback, qrUrl }: DeepLinkGeneratorCardProps) {
  const [copied, setCopied] = useState<string | null>(null);
  const copy = (label: string, text: string) => {
    navigator.clipboard?.writeText(text);
    setCopied(label);
    setTimeout(() => setCopied(null), 2000);
  };
  const links = [
    { label: "Deep Link", value: deepLink },
    { label: "Short Link", value: shortLink },
    { label: "Web Fallback", value: webFallback },
  ];
  return (
    <div className="space-y-3 rounded-lg border p-4 dark:border-gray-700">
      <h3 className="font-semibold">Deep Links</h3>
      {links.map(l => (
        <div key={l.label} className="flex items-center justify-between gap-2">
          <div className="min-w-0 flex-1">
            <p className="text-xs text-gray-400">{l.label}</p>
            <p className="truncate font-mono text-xs">{l.value}</p>
          </div>
          <button onClick={() => copy(l.label, l.value)}
            className="flex-shrink-0 rounded border px-2 py-1 text-xs dark:border-gray-600">
            {copied === l.label ? "Copied!" : "Copy"}
          </button>
        </div>
      ))}
    </div>
  );
}
