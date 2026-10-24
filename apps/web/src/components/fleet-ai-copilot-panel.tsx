"use client";
export function FleetAiCopilotPanel({ copilots, active, interactions, satisfaction }: { copilots: number; active: number; interactions: number; satisfaction: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 AI Copilot</h3>
    <div className="text-sm">{active}/{copilots} active · {interactions.toLocaleString()} interactions · {satisfaction}% satisfaction</div>
  </div>);
}
