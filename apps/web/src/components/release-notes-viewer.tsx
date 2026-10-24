"use client";

interface ReleaseNotesViewerProps { version: string; features: string[]; fixes: string[];
  breakingChanges: string[]; totalCommits: number; hasBreaking: boolean; }

export function ReleaseNotesViewer({ version, features, fixes, breakingChanges, totalCommits, hasBreaking }: ReleaseNotesViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📝 Release Notes</h3>
        <div className="flex items-center gap-2">
          {hasBreaking && <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-100 text-red-700">BREAKING</span>}
          <span className="text-xs text-gray-400">v{version} · {totalCommits} commits</span>
        </div>
      </div>
      <div className="p-4 space-y-3 text-xs">
        {features.length > 0 && (
          <div><div className="font-semibold text-green-600 mb-1">✨ Features</div>
            {features.map((f, i) => <div key={i} className="text-gray-600 dark:text-gray-400 pl-3">• {f}</div>)}</div>
        )}
        {fixes.length > 0 && (
          <div><div className="font-semibold text-blue-500 mb-1">🐛 Fixes</div>
            {fixes.map((f, i) => <div key={i} className="text-gray-600 dark:text-gray-400 pl-3">• {f}</div>)}</div>
        )}
        {breakingChanges.length > 0 && (
          <div><div className="font-semibold text-red-600 mb-1">⚠️ Breaking Changes</div>
            {breakingChanges.map((b, i) => <div key={i} className="text-red-500 pl-3">• {b}</div>)}</div>
        )}
      </div>
    </div>
  );
}
