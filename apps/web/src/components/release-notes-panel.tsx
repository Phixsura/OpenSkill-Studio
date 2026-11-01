"use client";

interface ReleaseNote {
  version: string;
  title: string;
  summary: string;
  features: string[];
  fixes: string[];
  breaking: string[];
  highlights: string[];
  contributors: string[];
}

export function ReleaseNotesPanel({ note }: { note: ReleaseNote }) {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-bold">{note.title}</h2>
        <span className="text-sm text-gray-500">{note.version}</span>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{note.summary}</p>
      </div>

      {note.highlights.length > 0 && (
        <div className="rounded-xl bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 p-3">
          <span className="text-sm font-semibold">🌟 Highlights</span>
          {note.highlights.map((h, i) => <p key={i} className="text-sm mt-1">{h}</p>)}
        </div>
      )}

      {note.breaking.length > 0 && (
        <div>
          <span className="text-sm font-semibold text-red-600">⚠️ Breaking Changes</span>
          {note.breaking.map((b, i) => <div key={i} className="text-sm text-red-500 mt-0.5">• {b}</div>)}
        </div>
      )}

      {note.features.length > 0 && (
        <div>
          <span className="text-sm font-semibold">✨ Features ({note.features.length})</span>
          {note.features.map((f, i) => <div key={i} className="text-sm text-gray-600 dark:text-gray-400 mt-0.5">• {f}</div>)}
        </div>
      )}

      {note.fixes.length > 0 && (
        <div>
          <span className="text-sm font-semibold">🐛 Fixes ({note.fixes.length})</span>
          {note.fixes.map((f, i) => <div key={i} className="text-sm text-gray-600 dark:text-gray-400 mt-0.5">• {f}</div>)}
        </div>
      )}

      {note.contributors.length > 0 && (
        <div className="text-sm text-gray-500">🙏 {note.contributors.join(", ")}</div>
      )}
    </div>
  );
}
