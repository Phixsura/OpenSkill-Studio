"use client";
export function FleetAiGpuPoolV2Panel({ pools, active, gpus, allocated, queue, utilization }: { pools: number; active: number; gpus: number; allocated: number; queue: number; utilization: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🖥️ AI GPU Pool v2</h3>
    <div className="text-sm">{active}/{pools} active · {allocated}/{gpus} GPUs ({utilization}%) · {queue} queued</div>
  </div>);
}
