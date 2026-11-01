"use client";

import { useState } from "react";

interface ChangelogStats { total: number; conventional: number; breaking: number; byType: Record<string, number>; }

export function ChangelogGenPanel({
  generatedMarkdown,
  stats,
  onGenerate,
}: {
  generatedMarkdown: string;
  stats: ChangelogStats | null;
  onGenerate?: (version: string) => void;
}) {
  const [version, setVersion] = useState("1.0.0");

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📋 Changelog Generator</h2>
      <div className="flex gap-2">
        <input type="text" value={version} onChange={(e) => setVersion(e.target.value)}
          placeholder="Version" className="rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm font-mono w-32" />
        <button onClick={() => onGenerate?.(version)}
          className="text-sm bg-green-600 text-white px-4 py-1.5 rounded-lg">Generate</button>
      </div>
      {stats && (
        <div className="flex gap-3 text-xs text-gray-500">
          <span>{stats.conventional}/{stats.total} conventional</span>
          {stats.breaking > 0 && <span className="text-red-500">{stats.breaking} breaking</span>}
          {Object.entries(stats.byType).map(([t, n]) => <span key={t}>{t}: {n}</span>)}
        </div>
      )}
      {generatedMarkdown && (
        <pre className="rounded-lg border dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50 p-3 text-xs overflow-auto max-h-64 whitespace-pre-wrap">
          {generatedMarkdown}
        </pre>
      )}
    </div>
  );
}
