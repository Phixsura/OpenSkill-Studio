"use client";
export function FleetAiPlatCiV2Panel({ pipelines, active, builds, passRate, duration }: { pipelines: number; active: number; builds: number; passRate: number; duration: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 AI CI v2</h3>
    <div className="text-sm">{active}/{pipelines} active · {builds.toLocaleString()} builds · {passRate}% pass · {duration}m avg</div>
  </div>);
}
