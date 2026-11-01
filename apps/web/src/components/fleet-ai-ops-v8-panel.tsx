"use client";
export function FleetAiOpsV8Panel({ systems, active, automations, autoResolved, toil }: { systems: number; active: number; automations: number; autoResolved: number; toil: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 AI Ops v8</h3>
    <div className="text-sm">{active}/{systems} active · {automations} automations · {autoResolved.toLocaleString()} auto-resolved · {toil}% toil↓</div>
  </div>);
}
