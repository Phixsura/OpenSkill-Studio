"use client";

interface VersionCompareViewProps { v1: string; v2: string; added: string[]; removed: string[]; breaking: boolean; sandboxChanged: boolean; }

export function VersionCompareView({ v1, v2, added, removed, breaking, sandboxChanged }: VersionCompareViewProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="mb-2 font-semibold">v{v1} → v{v2} {breaking && <span className="text-red-600">⚠️ Breaking</span>}</h4>
      {added.length > 0 && <div className="mb-1"><span className="text-xs text-green-600">+ {added.join(", ")}</span></div>}
      {removed.length > 0 && <div className="mb-1"><span className="text-xs text-red-600">- {removed.join(", ")}</span></div>}
      {sandboxChanged && <p className="text-xs text-yellow-600">⚙️ Sandbox changed</p>}
      {!added.length && !removed.length && !sandboxChanged && <p className="text-xs text-gray-400">No significant changes</p>}
    </div>
  );
}
