"use client";

import { useState } from "react";

interface CodeBlockProps { lines: string[]; language?: string; }

export function CodeBlock({ lines, language = "bash" }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);
  const code = lines.join("\n");
  const copy = () => { navigator.clipboard?.writeText(code); setCopied(true); setTimeout(() => setCopied(false), 2000); };
  return (
    <div className="relative rounded-lg bg-gray-900 p-4">
      <button onClick={copy} className="absolute right-2 top-2 rounded bg-gray-700 px-2 py-0.5 text-xs text-gray-300">{copied ? "✅" : "Copy"}</button>
      <pre className="overflow-x-auto text-sm text-green-400"><code>{code}</code></pre>
    </div>
  );
}
