"use client";
export function FleetAiShardPanel({ configs, active, shards, models, rebalances }: { configs: number; active: number; shards: number; models: number; rebalances: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔪 AI Model Sharding</h3>
    <div className="text-sm">{active}/{configs} active · {shards} shards · {models} models · {rebalances} rebalances</div>
  </div>);
}
