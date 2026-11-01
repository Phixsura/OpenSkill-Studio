"use client";
export function FleetAiFedLearnPanel({ clusters, active, participants, rounds, convergence }: { clusters: number; active: number; participants: number; rounds: number; convergence: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 AI Federated Learning</h3>
    <div className="text-sm">{active}/{clusters} active · {participants} nodes · {rounds} rounds · {(convergence * 100).toFixed(0)}% converged</div>
  </div>);
}
