"use client";
export function FleetAiComputeAllocV2Panel({ allocators, active, gpus, allocated, efficiency, costSaved }: { allocators: number; active: number; gpus: number; allocated: number; efficiency: number; costSaved: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🖥️ AI Compute Allocator v2</h3>
    <div className="text-sm">{active}/{allocators} active · {allocated}/{gpus} GPUs ({efficiency}%) · {costSaved}% cost saved</div>
  </div>);
}
