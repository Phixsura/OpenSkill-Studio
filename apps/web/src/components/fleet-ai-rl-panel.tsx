"use client";
export function FleetAiRlPanel({ environments, active, episodes, reward, convergence }: { environments: number; active: number; episodes: number; reward: number; convergence: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎮 AI Reinforcement Learning</h3>
    <div className="text-sm">{active}/{environments} active · {episodes.toLocaleString()} episodes · reward {reward} · {(convergence*100).toFixed(0)}% converged</div>
  </div>);
}
