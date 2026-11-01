"use client";
export function FleetAiAgentsPanel({ agents, running, tasks, tools }: { agents: number; running: number; tasks: number; tools: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 AI Agents</h3>
    <div className="text-sm">{running}/{agents} running · {tasks.toLocaleString()} tasks · {tools} tools</div>
  </div>);
}
