"use client";
export function FleetAiModelCostPanel({ trackers, active, models, cost, costPer1k }: { trackers: number; active: number; models: number; cost: number; costPer1k: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI Model Cost</h3>
    <div className="text-sm">{active}/{trackers} active · {models} models · ${cost.toLocaleString()} · ${costPer1k}/1K tokens</div>
  </div>);
}
