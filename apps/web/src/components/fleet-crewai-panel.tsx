"use client";
export function FleetCrewaiPanel({ crews, active, agents, tasks }: { crews: number; active: number; agents: number; tasks: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 CrewAI</h3>
    <div className="text-sm">{active}/{crews} active · {agents} agents · {tasks.toLocaleString()} tasks</div>
  </div>);
}
