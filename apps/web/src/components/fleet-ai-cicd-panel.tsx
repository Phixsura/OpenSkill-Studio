"use client";
export function FleetAiCicdPanel({ pipelines, active, builds, deploys, successRate }: { pipelines: number; active: number; builds: number; deploys: number; successRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 AI CI/CD</h3>
    <div className="text-sm">{active}/{pipelines} active · {builds} builds · {deploys} deploys · {successRate}% success</div>
  </div>);
}
