"use client";
export function FleetMlPipelineV9Panel({ pipelines, gpuHours }: { pipelines: number; gpuHours: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 ML Pipeline v9</h3>
    <div className="text-sm">{pipelines} pipelines · {gpuHours}h GPU</div>
  </div>);
}
