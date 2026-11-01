"use client";
export function FleetAiPipeOrchPanel({ orchestrators, active, pipelines, stages, successRate }: { orchestrators: number; active: number; pipelines: number; stages: number; successRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 AI Pipeline Orchestrator</h3>
    <div className="text-sm">{active}/{orchestrators} active · {pipelines.toLocaleString()} pipelines · {stages.toLocaleString()} stages · {successRate}%</div>
  </div>);
}
