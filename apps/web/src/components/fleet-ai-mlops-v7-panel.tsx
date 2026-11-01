"use client";
export function FleetAiMlopsV7Panel({ systems, active, modelsProd, experiments, deploys, health }: { systems: number; active: number; modelsProd: number; experiments: number; deploys: number; health: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 AI MLOps v7</h3>
    <div className="text-sm">{active}/{systems} active · {modelsProd} in prod · {experiments} experiments · {deploys} deploys · {health}% health</div>
  </div>);
}
