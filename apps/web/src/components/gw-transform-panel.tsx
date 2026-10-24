"use client";
interface GwTransformPanelProps { rulesApplied: string[]; totalRules: number; }
export function GwTransformPanel({ rulesApplied, totalRules }: GwTransformPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Gateway Transform</h3>
        <span className="text-xs text-gray-400">{rulesApplied.length}/{totalRules} rules applied</span>
      </div>
      <div className="p-4 text-xs font-mono space-y-0.5">
        {rulesApplied.map((r, i) => <div key={i} className="text-blue-500">{r}</div>)}
        {rulesApplied.length === 0 && <div className="text-gray-400">No transformations</div>}
      </div>
    </div>
  );
}
