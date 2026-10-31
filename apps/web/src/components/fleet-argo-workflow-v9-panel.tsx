"use client";
export function FleetArgoWorkflowV9Panel({ workflows, running }: { workflows: number; running: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Argo Workflow v9</h3>
    <div className="text-sm">{workflows} workflows · {running} running</div>
  </div>);
}
