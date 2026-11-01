"use client";
export function FleetAiEvalPanel({ pipelines, active, evaluations, metrics }: { pipelines: number; active: number; evaluations: number; metrics: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Evaluation</h3>
    <div className="text-sm">{active}/{pipelines} active · {evaluations.toLocaleString()} evals · {metrics} metrics</div>
  </div>);
}
