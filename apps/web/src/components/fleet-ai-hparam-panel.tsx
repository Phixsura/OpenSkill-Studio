"use client";
export function FleetAiHparamPanel({ tuners, active, trials, bestScore, dimensions }: { tuners: number; active: number; trials: number; bestScore: number; dimensions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎛️ AI Hyperparameter Tuning</h3>
    <div className="text-sm">{active}/{tuners} active · {trials.toLocaleString()} trials · best {bestScore} · {dimensions}D search</div>
  </div>);
}
