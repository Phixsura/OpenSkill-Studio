"use client";
export function FleetAiAutomatePanel({ workflows, active, automations, hoursSaved }: { workflows: number; active: number; automations: number; hoursSaved: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚙️ AI Automation</h3>
    <div className="text-sm">{active}/{workflows} active · {automations.toLocaleString()} automations · {hoursSaved.toLocaleString()}h saved</div>
  </div>);
}
