"use client";
export function FleetBuildpacksPanel({ total, usingBp, usingDockerfile, avgBuild }: { total: number; usingBp: number; usingDockerfile: number; avgBuild: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 Buildpacks</h3>
    <div className="text-sm">{usingBp} buildpacks · {usingDockerfile} Dockerfile · avg {avgBuild}s</div>
  </div>);
}
