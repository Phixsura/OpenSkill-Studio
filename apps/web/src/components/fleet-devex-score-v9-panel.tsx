"use client";
export function FleetDevexScoreV9Panel({ teams, score }: { teams: number; score: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💻 DevEx Score v9</h3>
    <div className="text-sm">{teams} teams · {score}/100 score</div>
  </div>);
}
