"use client";
export function FleetAiWorkflowPanel({ workflows, active, executions, steps }: { workflows: number; active: number; executions: number; steps: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 AI Workflow</h3>
    <div className="text-sm">{active}/{workflows} active · {executions.toLocaleString()} exec · {steps} steps</div>
  </div>);
}
