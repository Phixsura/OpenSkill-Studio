"use client";
export function FleetAiFlashAttnPanel({ implementations, active, speedup, memorySaved, maxSeqLen }: { implementations: number; active: number; speedup: number; memorySaved: number; maxSeqLen: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ AI Flash Attention</h3>
    <div className="text-sm">{active}/{implementations} active · {speedup}x speed · {memorySaved}% mem saved · {(maxSeqLen/1000).toFixed(0)}K seq</div>
  </div>);
}
