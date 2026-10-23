"use client";

import { useState } from "react";

interface CopyButtonProps { text: string; label?: string; variant?: "icon" | "button"; }

export function CopyButton({ text, label = "Copy", variant = "button" }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard?.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (variant === "icon") {
    return (
      <button onClick={handleCopy} title="Copy to clipboard"
        className="rounded p-1 text-xs text-gray-400 hover:text-blue-500">
        {copied ? "✓" : "📋"}
      </button>
    );
  }
  return (
    <button onClick={handleCopy}
      className={`rounded border px-3 py-1.5 text-xs transition-colors ${copied ? "border-green-300 bg-green-50 text-green-700 dark:border-green-700 dark:bg-green-900/10" : "dark:border-gray-600"}`}>
      {copied ? "Copied! ✓" : label}
    </button>
  );
}
