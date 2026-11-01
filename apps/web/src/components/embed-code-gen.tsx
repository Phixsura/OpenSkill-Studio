"use client";
import { useState } from "react";

interface EmbedStyle { id: string; label: string; preview: string; }
interface EmbedCodeGenProps { appName: string; styles: EmbedStyle[];
  iframeCode: string; embedUrl: string;
  onStyleChange: (style: string) => void; }

export function EmbedCodeGen({ appName, styles, iframeCode, embedUrl, onStyleChange }: EmbedCodeGenProps) {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard?.writeText(iframeCode).then(() => { setCopied(true); setTimeout(() => setCopied(false), 2000); });
  };
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🔗 Embed Widget</h3>
      <p className="text-xs text-gray-400 mb-3">Share {appName} on your website</p>
      <div className="flex gap-2 mb-3">
        {styles.map(s => (
          <button key={s.id} onClick={() => onStyleChange(s.id)}
            className="text-xs px-3 py-1.5 rounded bg-gray-100 dark:bg-gray-800 hover:bg-blue-100 capitalize">{s.label}</button>
        ))}
      </div>
      <div className="bg-gray-900 rounded-lg p-3 mb-2">
        <code className="text-xs text-green-400 break-all">{iframeCode}</code>
      </div>
      <button onClick={handleCopy}
        className="w-full py-1.5 border rounded text-xs hover:bg-gray-50 dark:hover:bg-gray-800">
        {copied ? "✓ Copied!" : "📋 Copy Embed Code"}
      </button>
    </div>
  );
}
