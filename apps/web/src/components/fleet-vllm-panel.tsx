"use client";
export function FleetVllmPanel({ instances, running, tokensPerSec, gpus }: { instances: number; running: number; tokensPerSec: number; gpus: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ vLLM</h3>
    <div className="text-sm">{running}/{instances} running · {tokensPerSec.toLocaleString()} tok/s · {gpus} GPUs</div>
  </div>);
}
