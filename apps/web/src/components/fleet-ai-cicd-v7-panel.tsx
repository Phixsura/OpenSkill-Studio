"use client";
export function FleetAiCicdV7Panel({ pipelines, active, builds, deploys, passRate, duration }: { pipelines: number; active: number; builds: number; deploys: number; passRate: number; duration: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 AI CI/CD v7</h3>
    <div className="text-sm">{active}/{pipelines} active · {builds.toLocaleString()} builds · {deploys} deploys · {passRate}% · {duration}m</div>
  </div>);
}
