"use client";
export function FleetAiSreAutoPanel({ systems, active, toilReduced, automations, hoursSaved }: { systems: number; active: number; toilReduced: number; automations: number; hoursSaved: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 AI SRE Automation</h3>
    <div className="text-sm">{active}/{systems} active · {toilReduced}% toil reduced · {automations} automations · {hoursSaved.toLocaleString()}h saved</div>
  </div>);
}
