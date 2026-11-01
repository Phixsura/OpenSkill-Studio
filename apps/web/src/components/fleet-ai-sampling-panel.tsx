"use client";
export function FleetAiSamplingPanel({ samplers, active, rate, sampled, saved }: { samplers: number; active: number; rate: number; sampled: number; saved: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎲 AI Sampling</h3>
    <div className="text-sm">{active}/{samplers} active · {rate}% rate · {sampled.toLocaleString()} sampled · {saved}% storage saved</div>
  </div>);
}
