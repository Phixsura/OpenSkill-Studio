"use client";

import { useState } from "react";

interface AppCopyIdButtonProps { id: string; label?: string; }

export function AppCopyIdButton({ id, label = "Copy ID" }: AppCopyIdButtonProps) {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard?.writeText(id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button onClick={handleCopy} className="inline-flex items-center gap-1 rounded border border-gray-300 px-2 py-0.5 text-xs hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-800"
      title={id}>
      {copied ? "✅ Copied!" : `📋 ${label}`}
    </button>
  );
}
