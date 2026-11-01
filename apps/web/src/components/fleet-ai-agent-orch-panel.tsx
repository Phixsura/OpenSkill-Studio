"use client";
export function FleetAiAgentOrchPanel({ orchestrators, active, agents, tasks, successRate }: { orchestrators: number; active: number; agents: number; tasks: number; successRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 AI Agent Orchestrator</h3>
    <div className="text-sm">{active}/{orchestrators} active · {agents} agents · {tasks.toLocaleString()} tasks · {successRate}% success</div>
  </div>);
}
