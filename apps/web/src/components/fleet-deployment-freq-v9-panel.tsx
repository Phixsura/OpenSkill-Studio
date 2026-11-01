"use client";
export function FleetDeploymentFreqV9Panel({ teams, deploys }: { teams: number; deploys: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 Deploy Frequency v9</h3>
    <div className="text-sm">{teams} teams · {deploys} deploys today</div>
  </div>);
}
