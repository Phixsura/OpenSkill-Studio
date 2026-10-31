"use client";
export function FleetAiMemoryPanel({ stores, active, memories, retrievals }: { stores: number; active: number; memories: number; retrievals: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧠 AI Memory</h3>
    <div className="text-sm">{active}/{stores} active · {memories.toLocaleString()} memories · {retrievals.toLocaleString()} retrievals</div>
  </div>);
}
