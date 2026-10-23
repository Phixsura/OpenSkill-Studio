"use client";

interface Change { description: string; type?: string; breaking?: boolean; }
interface VersionComparisonViewProps {
  versionA: string; versionB: string;
  onlyInA: Change[]; onlyInB: Change[]; common: Change[];
  permsAdded: string[]; permsRemoved: string[];
  hasBreaking: boolean; migrationNotes: string[];
}

export function VersionComparisonView({ versionA, versionB, onlyInA, onlyInB, common, permsAdded, permsRemoved, hasBreaking, migrationNotes }: VersionComparisonViewProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">{versionA} → {versionB}</h3>
        {hasBreaking && <span className="rounded bg-red-100 px-2 py-0.5 text-xs text-red-700">Breaking</span>}
      </div>
      <div className="mt-3 grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs font-medium text-red-600">Removed in {versionB}</p>
          {onlyInA.map((c, i) => <p key={i} className="text-xs text-gray-500">- {c.description}</p>)}
          {onlyInA.length === 0 && <p className="text-xs text-gray-400">None</p>}
        </div>
        <div>
          <p className="text-xs font-medium text-green-600">Added in {versionB}</p>
          {onlyInB.map((c, i) => <p key={i} className="text-xs text-gray-500">+ {c.description}</p>)}
          {onlyInB.length === 0 && <p className="text-xs text-gray-400">None</p>}
        </div>
      </div>
      {(permsAdded.length > 0 || permsRemoved.length > 0) && (
        <div className="mt-3 rounded bg-yellow-50 p-2 dark:bg-yellow-900/20">
          <p className="text-xs font-medium">Permission Changes</p>
          {permsAdded.map(p => <p key={p} className="text-xs text-green-600">+ {p}</p>)}
          {permsRemoved.map(p => <p key={p} className="text-xs text-red-600">- {p}</p>)}
        </div>
      )}
      <div className="mt-3 space-y-0.5">
        {migrationNotes.map((n, i) => <p key={i} className="text-xs text-gray-600 dark:text-gray-400">{n}</p>)}
      </div>
    </div>
  );
}
