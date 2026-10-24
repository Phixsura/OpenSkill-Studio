"use client";
export function FleetAiChaosV7Panel({ systems, active, experiments, blast, recovery }: { systems: number; active: number; experiments: number; blast: number; recovery: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌪️ AI Chaos v7</h3>
    <div className="text-sm">{active}/{systems} active · {experiments} experiments · {blast}% blast · {recovery}s recovery</div>
  </div>);
}
