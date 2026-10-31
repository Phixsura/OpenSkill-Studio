"use client";
export function FleetApiDeploymentPipelineV9Panel({ pipelines, success }: { pipelines: number; success: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 Deploy Pipeline v9</h3>
    <div className="text-sm">{pipelines} pipelines · {success} succeeded</div>
  </div>);
}
