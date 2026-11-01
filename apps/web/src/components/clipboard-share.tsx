"use client";

import { useState } from "react";

interface ShareOption { label: string; value: string; icon: string; }
interface ClipboardShareProps { options: ShareOption[]; }

export function ClipboardShare({ options }: ClipboardShareProps) {
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);
  const copy = (value: string, idx: number) => {
    navigator.clipboard?.writeText(value);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold">Share</h3>
      {options.map((opt, i) => (
        <div key={i} className="flex items-center gap-2 rounded-lg border p-3 dark:border-gray-700">
          <span>{opt.icon}</span>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium">{opt.label}</p>
            <p className="text-xs text-gray-400 truncate font-mono">{opt.value}</p>
          </div>
          <button onClick={() => copy(opt.value, i)}
            className="shrink-0 rounded bg-gray-100 px-2.5 py-1 text-xs dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700">
            {copiedIdx === i ? "✓ Copied" : "Copy"}
          </button>
        </div>
      ))}
    </div>
  );
}
