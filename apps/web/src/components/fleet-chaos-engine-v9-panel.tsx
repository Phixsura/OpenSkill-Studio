"use client";
export function FleetChaosEngineV9Panel({ experiments, completed }: { experiments: number; completed: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌪️ Chaos Engine v9</h3>
    <div className="text-sm">{experiments} experiments · {completed} completed</div>
  </div>);
}
