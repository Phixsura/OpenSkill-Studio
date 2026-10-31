"use client";
export function FleetAiPipeV3Panel({ pipelines, active, stages, executions, successRate }: { pipelines: number; active: number; stages: number; executions: number; successRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 AI Pipeline v3</h3>
    <div className="text-sm">{active}/{pipelines} active · {stages} stages · {executions.toLocaleString()} exec · {successRate}% success</div>
  </div>);
}
