"use client";
export function FleetAiOpsV9Panel({ systems, active, automations, tasks, toil }: { systems: number; active: number; automations: number; tasks: number; toil: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 AI Ops v9</h3>
    <div className="text-sm">{active}/{systems} active · {automations.toLocaleString()} automations · {tasks.toLocaleString()} tasks · {toil}% toil↓</div>
  </div>);
}
