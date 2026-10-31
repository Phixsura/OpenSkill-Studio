"use client";
export function FleetAiSpecDecPanel({ decoders, active, tokens, acceptanceRate, speedup }: { decoders: number; active: number; tokens: number; acceptanceRate: number; speedup: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ AI Speculative Decoding</h3>
    <div className="text-sm">{active}/{decoders} active · {tokens.toLocaleString()} tok · {acceptanceRate}% accept · {speedup}x speed</div>
  </div>);
}
