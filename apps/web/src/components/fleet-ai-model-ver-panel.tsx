"use client";
export function FleetAiModelVerPanel({ versioners, active, models, versions, rollbacks }: { versioners: number; active: number; models: number; versions: number; rollbacks: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏷️ AI Model Versioner</h3>
    <div className="text-sm">{active}/{versioners} active · {models} models · {versions} versions · {rollbacks} rollbacks</div>
  </div>);
}
