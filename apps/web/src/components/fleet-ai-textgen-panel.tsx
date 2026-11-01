"use client";
export function FleetAiTextgenPanel({ services, active, generations, tokens }: { services: number; active: number; generations: number; tokens: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✍️ AI Text Gen</h3>
    <div className="text-sm">{active}/{services} active · {generations.toLocaleString()} gens · {tokens.toLocaleString()} tokens</div>
  </div>);
}
