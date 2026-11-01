"use client";

import { useState } from "react";

interface CopyPreviewProps { copies: Record<string, string>; appName: string; }

const templateLabels: Record<string, string> = {
  hero: "🎯 Hero", cta: "🔘 CTA", feature: "✨ Feature", social: "📱 Social",
};

export function CopyPreview({ copies, appName }: CopyPreviewProps) {
  const [copied, setCopied] = useState<string | null>(null);
  const copy = (key: string, text: string) => {
    navigator.clipboard?.writeText(text);
    setCopied(key);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">Marketing Copy — {appName}</h3>
      {Object.entries(copies).map(([key, text]) => (
        <div key={key} className="rounded-lg border p-3 dark:border-gray-700">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-medium">{templateLabels[key] ?? key}</span>
            <button onClick={() => copy(key, text)}
              className="text-xs text-gray-400 hover:text-gray-600">{copied === key ? "✓" : "Copy"}</button>
          </div>
          <p className="text-sm">{text}</p>
        </div>
      ))}
    </div>
  );
}
