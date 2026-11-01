"use client";
export function FleetMlflowPanel({ servers, running, experiments, runs, models }: { servers: number; running: number; experiments: number; runs: number; models: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 MLflow</h3>
    <div className="text-sm">{running}/{servers} running · {experiments} exps · {runs} runs · {models} models</div>
  </div>);
}
