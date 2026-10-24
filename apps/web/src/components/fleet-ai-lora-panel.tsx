"use client";
export function FleetAiLoraPanel({ adapters, active, rank, trained, paramPct }: { adapters: number; active: number; rank: number; trained: number; paramPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔗 AI LoRA Adapter</h3>
    <div className="text-sm">{active}/{adapters} active · rank {rank} · {trained} trained · {paramPct}% params</div>
  </div>);
}
