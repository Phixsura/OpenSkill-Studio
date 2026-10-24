"use client";

interface SchemaChange { field: string; old: string; new: string; }
interface SchemaVersionDiffProps { added: string[]; removed: string[];
  changed: SchemaChange[]; breaking: boolean; suggestedBump: string; }

export function SchemaVersionDiff({ added, removed, changed, breaking, suggestedBump }: SchemaVersionDiffProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Schema Diff</h3>
        <div className="flex items-center gap-2">
          {breaking && <span className="text-xs text-red-500 font-bold">BREAKING</span>}
          <span className="text-xs px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-800">{suggestedBump}</span>
        </div>
      </div>
      <div className="p-4 space-y-2 text-xs font-mono">
        {added.map(f => <div key={f} className="text-green-600">+ {f}</div>)}
        {removed.map(f => <div key={f} className="text-red-600">- {f}</div>)}
        {changed.map(c => (
          <div key={c.field} className="text-yellow-600">~ {c.field}: {c.old} → {c.new}</div>
        ))}
        {added.length === 0 && removed.length === 0 && changed.length === 0 && (
          <div className="text-gray-400 text-center">No changes</div>
        )}
      </div>
    </div>
  );
}
