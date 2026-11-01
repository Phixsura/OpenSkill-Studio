"use client";
interface Change { type: string; description: string; }
interface SvcChangelogProps { versions: Record<string, Change[]>; totalChanges: number; }
export function SvcChangelog({ versions, totalChanges }: SvcChangelogProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📝 Changelog</h3>
        <span className="text-xs text-gray-400">{totalChanges} changes</span>
      </div>
      <div className="p-4 space-y-3 text-xs">
        {Object.entries(versions).map(([v, changes]) => (
          <div key={v}><div className="font-bold mb-1">v{v}</div>
            {changes.map((c, i) => <div key={i} className="text-gray-500 pl-2">• [{c.type}] {c.description}</div>)}
          </div>
        ))}
      </div>
    </div>
  );
}
