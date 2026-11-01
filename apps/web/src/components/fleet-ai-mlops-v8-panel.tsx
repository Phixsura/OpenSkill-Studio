"use client";
export function FleetAiMlopsV8Panel({ systems, active, models, experiments, deploys, health }: { systems: number; active: number; models: number; experiments: number; deploys: number; health: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 AI MLOps v8</h3>
    <div className="text-sm">{active}/{systems} active · {models} models · {experiments} experiments · {deploys} deploys · {health}% health</div>
  </div>);
}
