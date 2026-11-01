"use client";
export function FleetAiResAllocPanel({ allocators, active, gpus, allocated, waste }: { allocators: number; active: number; gpus: number; allocated: number; waste: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🖥️ AI Resource Allocator</h3>
    <div className="text-sm">{active}/{allocators} active · {allocated}/{gpus} GPUs · {waste}% waste</div>
  </div>);
}
