"use client";
export function FleetAiAgentFwPanel({ frameworks, active, agents, tasks }: { frameworks: number; active: number; agents: number; tasks: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 AI Agent FW</h3>
    <div className="text-sm">{active}/{frameworks} active · {agents} agents · {tasks.toLocaleString()} tasks</div>
  </div>);
}
