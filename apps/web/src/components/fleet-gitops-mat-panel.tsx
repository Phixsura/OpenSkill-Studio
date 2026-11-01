"use client";
export function FleetGitopsMatPanel({ score, level }: { score: number; level: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4 text-center">
    <h3 className="font-semibold mb-1">🔄 GitOps Maturity</h3>
    <div className="text-2xl font-black text-blue-600">{score} — {level}</div>
  </div>);
}
