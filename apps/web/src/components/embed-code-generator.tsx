"use client";
import { useState } from "react";

interface EmbedOptions { extensionId: string; themes: string[]; sizes: string[]; }

export function EmbedCodeGenerator({ options }: { options: EmbedOptions }) {
  const [theme, setTheme] = useState("auto");
  const [size, setSize] = useState("medium");
  const [format, setFormat] = useState<"html" | "iframe" | "markdown">("iframe");
  const [copied, setCopied] = useState(false);

  const code = format === "iframe"
    ? `<iframe src="https://marketplace.openskill.dev/embed/${options.extensionId}?theme=${theme}" width="${size === "small" ? 200 : size === "large" ? 400 : 300}" height="120" frameborder="0"></iframe>`
    : format === "markdown"
    ? `[![Extension](https://marketplace.openskill.dev/badge/${options.extensionId})](https://marketplace.openskill.dev/ext/${options.extensionId})`
    : `<div data-osk-ext="${options.extensionId}" data-theme="${theme}" data-size="${size}"></div><script src="https://marketplace.openskill.dev/embed.js"></script>`;

  return (
    <div className="space-y-3">
      <h3 className="font-bold text-sm">Embed Widget</h3>
      <div className="flex gap-2">
        {(["iframe", "html", "markdown"] as const).map(f => (
          <button key={f} onClick={() => setFormat(f)}
            className={`text-xs px-3 py-1 rounded-full uppercase ${format === f ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{f}</button>
        ))}
      </div>
      <div className="flex gap-2">
        {options.themes.map(t => (
          <button key={t} onClick={() => setTheme(t)}
            className={`text-xs px-2 py-1 rounded capitalize ${theme === t ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{t}</button>
        ))}
      </div>
      <pre className="bg-gray-900 text-green-400 rounded-xl p-3 text-xs font-mono overflow-x-auto">{code}</pre>
      <button onClick={() => { navigator.clipboard?.writeText(code); setCopied(true); setTimeout(() => setCopied(false), 2000); }}
        className="text-xs bg-blue-500 text-white px-3 py-1.5 rounded-lg">{copied ? "✓ Copied!" : "📋 Copy Code"}</button>
    </div>
  );
}
