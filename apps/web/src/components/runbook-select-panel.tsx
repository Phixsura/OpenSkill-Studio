"use client";
interface RunbookMatch { runbook: string; score: number; steps: number; }
interface RunbookSelectPanelProps { selected: string | null; confidence: number;
  alternatives: RunbookMatch[]; totalMatches: number; }
export function RunbookSelectPanel({ selected, confidence, alternatives, totalMatches }: RunbookSelectPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📖 Runbook Selector</h3>
        <span className="text-xs text-gray-400">{totalMatches} matches</span>
      </div>
      <div className="p-4 text-xs">
        {selected ? (
          <div>
            <div className="font-bold text-blue-500 mb-1">Selected: {selected} (confidence: {confidence})</div>
            {alternatives.length > 0 && (
              <div className="text-gray-400">Also: {alternatives.map(a => a.runbook).join(", ")}</div>
            )}
          </div>
        ) : (
          <div className="text-yellow-600">No matching runbook found</div>
        )}
      </div>
    </div>
  );
}
