"use client";

interface VersionCompareViewProps { fromVersion: string; toVersion: string;
  added: string[]; removed: string[]; unchanged: string[];
  breaking: boolean; summary: string; }

export function VersionCompareView({ fromVersion, toVersion, added, removed, unchanged, breaking, summary }: VersionCompareViewProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🔄 Version Comparison</h3>
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono">{fromVersion} → {toVersion}</span>
          {breaking && <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700">Breaking</span>}
        </div>
      </div>
      <div className="text-xs text-gray-400 mb-3">{summary}</div>
      <div className="grid grid-cols-3 gap-3">
        <div>
          <h4 className="text-xs font-semibold text-green-600 mb-1">+ Added ({added.length})</h4>
          {added.map(f => <p key={f} className="text-sm text-green-600">+ {f}</p>)}
        </div>
        <div>
          <h4 className="text-xs font-semibold text-red-600 mb-1">- Removed ({removed.length})</h4>
          {removed.map(f => <p key={f} className="text-sm text-red-600">- {f}</p>)}
        </div>
        <div>
          <h4 className="text-xs font-semibold text-gray-400 mb-1">= Unchanged ({unchanged.length})</h4>
          {unchanged.map(f => <p key={f} className="text-sm text-gray-400">{f}</p>)}
        </div>
      </div>
    </div>
  );
}
