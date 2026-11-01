"use client";

interface PlatformRelease {
  version: string; date: string; title: string;
  features: string[]; fixes: string[]; breaking: string[];
}

export function PlatformChangelogPanel({ releases }: { releases: PlatformRelease[] }) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📋 Platform Changelog</h2>
      {releases.map((r) => (
        <div key={r.version} className="rounded-xl border dark:border-gray-700 p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="font-bold text-lg">{r.version}</span>
            <span className="text-sm text-gray-500">{r.date}</span>
            <span className="font-semibold text-sm">{r.title}</span>
          </div>
          {r.breaking.length > 0 && (
            <div className="mb-2">
              <span className="text-xs font-bold text-red-600">⚠ Breaking</span>
              {r.breaking.map((b, i) => <div key={i} className="text-xs text-red-500 ml-3">• {b}</div>)}
            </div>
          )}
          {r.features.length > 0 && (
            <div className="mb-1">
              <span className="text-xs font-bold text-green-600">✨ Features</span>
              {r.features.map((f, i) => <div key={i} className="text-xs text-gray-600 dark:text-gray-400 ml-3">• {f}</div>)}
            </div>
          )}
          {r.fixes.length > 0 && (
            <div>
              <span className="text-xs font-bold text-blue-600">🐛 Fixes</span>
              {r.fixes.map((f, i) => <div key={i} className="text-xs text-gray-600 dark:text-gray-400 ml-3">• {f}</div>)}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
