"use client";
export function FleetAiWfEnginePanel({ engines, active, workflows, steps, duration }: { engines: number; active: number; workflows: number; steps: number; duration: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚙️ AI Workflow Engine</h3>
    <div className="text-sm">{active}/{engines} active · {workflows.toLocaleString()} workflows · {steps.toLocaleString()} steps · {duration}s avg</div>
  </div>);
}
