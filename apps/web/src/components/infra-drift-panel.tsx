"use client";
interface DriftItem { resource: string; changes: Record<string, { desired: unknown; actual: unknown }>; }
interface InfraDriftPanelProps { drifted: DriftItem[]; missing: string[]; extra: string[];
  hasDrift: boolean; totalIssues: number; }
export function InfraDriftPanel({ drifted, missing, extra, hasDrift, totalIssues }: InfraDriftPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔀 Infrastructure Drift</h3>
        <span className={`text-xs font-bold ${hasDrift ? "text-red-500" : "text-green-600"}`}>
          {hasDrift ? `⚠ ${totalIssues} issues` : "✅ No drift"}
        </span>
      </div>
      {hasDrift && (
        <div className="p-4 text-xs font-mono space-y-0.5">
          {missing.map(m => <div key={m} className="text-red-600">- missing: {m}</div>)}
          {extra.map(e => <div key={e} className="text-yellow-600">+ extra: {e}</div>)}
          {drifted.map(d => (
            <div key={d.resource} className="text-orange-500">
              ~ {d.resource}: {Object.keys(d.changes).join(", ")} changed
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
