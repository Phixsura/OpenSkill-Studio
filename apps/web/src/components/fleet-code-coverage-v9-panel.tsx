"use client";
export function FleetCodeCoverageV9Panel({ repos, coverage }: { repos: number; coverage: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Code Coverage v9</h3>
    <div className="text-sm">{repos} repos · {coverage}% avg coverage</div>
  </div>);
}
