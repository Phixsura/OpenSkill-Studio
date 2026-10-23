"use client";
import { useState } from "react";

interface CopyButtonProps { value: string; display: string; label: string; sensitive: boolean; }

export function CopyButton({ value, display, label, sensitive }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);
  const [revealed, setRevealed] = useState(false);
  const handleCopy = () => {
    navigator.clipboard?.writeText(value).then(() => { setCopied(true); setTimeout(() => setCopied(false), 2000); });
  };
  const shown = sensitive && !revealed ? display : value;
  return (
    <div className="flex items-center gap-2 bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
      {label && <span className="text-xs text-gray-400 shrink-0">{label}</span>}
      <code className="text-xs font-mono flex-1 truncate">{shown}</code>
      {sensitive && (
        <button onClick={() => setRevealed(!revealed)}
          className="text-xs text-gray-400 hover:text-gray-600 shrink-0">{revealed ? "🙈" : "👁️"}</button>
      )}
      <button onClick={handleCopy}
        className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 shrink-0">
        {copied ? "✓" : "Copy"}
      </button>
    </div>
  );
}
