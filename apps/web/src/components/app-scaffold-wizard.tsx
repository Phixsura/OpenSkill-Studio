"use client";

import { useState } from "react";

interface ScaffoldFile { path: string; type: string; }
interface AppScaffoldWizardProps { files: ScaffoldFile[]; appName: string; runtime: string;
  features: string[]; onGenerate: () => void; }

const typeIcons: Record<string, string> = {
  source: "📄", config: "⚙️", test: "🧪", docs: "📝", ci: "🔄",
};

export function AppScaffoldWizard({ files, appName, runtime, features, onGenerate }: AppScaffoldWizardProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold">Scaffold: {appName}</h3>
          <p className="text-xs text-gray-400">{runtime} · {files.length} files · {features.length} features</p>
        </div>
        <button onClick={onGenerate} className="rounded bg-green-600 px-4 py-1.5 text-sm text-white">Generate</button>
      </div>
      <div className="rounded-lg border dark:border-gray-700 divide-y dark:divide-gray-700">
        {files.map(f => (
          <div key={f.path} className="flex items-center gap-2 px-4 py-2">
            <span className="text-xs">{typeIcons[f.type] ?? "📄"}</span>
            <code className="text-sm font-mono">{f.path}</code>
          </div>
        ))}
      </div>
    </div>
  );
}
