"use client";
export function FleetAiOpsAutoV2Panel({ systems, active, automations, tasks, manual }: { systems: number; active: number; automations: number; tasks: number; manual: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 AI Ops Automation v2</h3>
    <div className="text-sm">{active}/{systems} active · {automations} automations · {tasks.toLocaleString()} tasks · {manual} manual</div>
  </div>);
}
