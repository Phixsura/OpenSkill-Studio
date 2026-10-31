"use client";
export function FleetAiBenchV2Panel({ benches, active, models, tasks, entries }: { benches: number; active: number; models: number; tasks: number; entries: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📏 AI Benchmark v2</h3>
    <div className="text-sm">{active}/{benches} active · {models} models · {tasks} tasks · {entries} entries</div>
  </div>);
}
