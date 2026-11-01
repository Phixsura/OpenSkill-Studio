"use client";

import { useState } from "react";

interface GeneratedFile {
  path: string;
  size: number;
  isEntrypoint: boolean;
}

interface ScaffoldResult {
  extensionName: string;
  runtime: string;
  files: GeneratedFile[];
}

const runtimes = [
  { value: "node20", label: "Node.js 20", icon: "🟢" },
  { value: "python3.12", label: "Python 3.12", icon: "🐍" },
  { value: "deno", label: "Deno", icon: "🦕" },
];

export function CLIScaffoldPanel({
  result,
  onGenerate,
  onDownload,
}: {
  result: ScaffoldResult | null;
  onGenerate?: (name: string, runtime: string) => void;
  onDownload?: () => void;
}) {
  const [name, setName] = useState("");
  const [runtime, setRuntime] = useState("node20");

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🏗️ Scaffold Extension</h2>

      <div className="rounded-lg border dark:border-gray-700 p-4 space-y-3">
        <div>
          <label className="text-xs text-gray-500 block mb-1">Extension Name</label>
          <input type="text" value={name} onChange={(e) => setName(e.target.value)}
            placeholder="my-awesome-extension"
            className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm font-mono" />
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-1">Runtime</label>
          <div className="flex gap-2">
            {runtimes.map((r) => (
              <button key={r.value} onClick={() => setRuntime(r.value)}
                className={`flex items-center gap-1 text-sm px-3 py-2 rounded-lg border ${runtime === r.value ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20" : "dark:border-gray-700"}`}>
                <span>{r.icon}</span> {r.label}
              </button>
            ))}
          </div>
        </div>
        <button onClick={() => onGenerate?.(name, runtime)}
          disabled={!name.trim()}
          className="w-full text-sm bg-blue-600 text-white py-2 rounded-lg disabled:opacity-50">
          Generate Project
        </button>
      </div>

      {result && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold">Generated: {result.extensionName}</span>
            <button onClick={onDownload}
              className="text-xs bg-green-600 text-white px-3 py-1 rounded-lg">Download ZIP</button>
          </div>
          <div className="rounded-lg border dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50 p-3 space-y-0.5">
            {result.files.map((f) => (
              <div key={f.path} className="flex items-center gap-2 text-xs">
                <span className="text-gray-400">{f.isEntrypoint ? "▶" : "📄"}</span>
                <code className={f.isEntrypoint ? "font-bold" : ""}>{f.path}</code>
                <span className="text-gray-400 ml-auto">{f.size}B</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
