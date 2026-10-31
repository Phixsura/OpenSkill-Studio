"use client";
export function FleetAiChaosV8Panel({ systems, active, experiments, recovery, blast }: { systems: number; active: number; experiments: number; recovery: number; blast: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌪️ AI Chaos v8</h3>
    <div className="text-sm">{active}/{systems} active · {experiments} experiments · {recovery}s recovery · {blast}% blast</div>
  </div>);
}
