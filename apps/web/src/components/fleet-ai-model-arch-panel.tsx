"use client";
export function FleetAiModelArchPanel({ archives, active, models, storageTb, retrievals }: { archives: number; active: number; models: number; storageTb: number; retrievals: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏛️ AI Model Archive</h3>
    <div className="text-sm">{active}/{archives} active · {models.toLocaleString()} models · {storageTb}TB · {retrievals} retrievals</div>
  </div>);
}
