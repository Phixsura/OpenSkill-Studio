"use client";
export function FleetAiContPretrainPanel({ jobs, active, tokens, loss, gpus }: { jobs: number; active: number; tokens: number; loss: number; gpus: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏋️ AI Continuous Pretraining</h3>
    <div className="text-sm">{active}/{jobs} active · {(tokens/1e12).toFixed(1)}T tokens · loss {loss} · {gpus} GPUs</div>
  </div>);
}
