"use client";

interface ConfigChange { key: string; old: unknown; new: unknown; }
interface VersionDiffProps { oldVersion: string; newVersion: string;
  featuresAdded: string[]; featuresRemoved: string[];
  permissionsAdded: string[]; permissionsRemoved: string[];
  configChanges: ConfigChange[]; hasBreaking: boolean; totalChanges: number; }

export function VersionDiff({ oldVersion, newVersion, featuresAdded, featuresRemoved,
  permissionsAdded, permissionsRemoved, configChanges, hasBreaking, totalChanges }: VersionDiffProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">v{oldVersion} → v{newVersion}</h3>
        <div className="flex items-center gap-2">
          {hasBreaking && <span className="rounded bg-red-100 px-2 py-0.5 text-xs text-red-700 dark:bg-red-900/30">Breaking</span>}
          <span className="text-xs text-gray-400">{totalChanges} changes</span>
        </div>
      </div>
      {featuresAdded.length > 0 && <div className="space-y-0.5">{featuresAdded.map(f => <p key={f} className="text-xs text-green-600">+ {f}</p>)}</div>}
      {featuresRemoved.length > 0 && <div className="space-y-0.5">{featuresRemoved.map(f => <p key={f} className="text-xs text-red-600 line-through">- {f}</p>)}</div>}
      {permissionsAdded.length > 0 && <div><p className="text-xs text-gray-400">New permissions:</p>{permissionsAdded.map(p => <p key={p} className="text-xs text-green-600">🔐 + {p}</p>)}</div>}
      {configChanges.length > 0 && <div><p className="text-xs text-gray-400">Config changes:</p>{configChanges.map(c => <p key={c.key} className="text-xs"><code>{c.key}</code>: {JSON.stringify(c.old)} → {JSON.stringify(c.new)}</p>)}</div>}
    </div>
  );
}
