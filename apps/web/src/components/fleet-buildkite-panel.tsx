"use client";
export function FleetBuildkitePanel({ pipelines, passing, agents, avgQueue }: { pipelines: number; passing: number; agents: number; avgQueue: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔨 Buildkite</h3>
    <div className="text-sm">{passing}/{pipelines} passing · {agents} agents · {avgQueue}s queue</div>
  </div>);
}
