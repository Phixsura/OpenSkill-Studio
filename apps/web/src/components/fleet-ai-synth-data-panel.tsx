"use client";
export function FleetAiSynthDataPanel({ generators, active, samples, quality }: { generators: number; active: number; samples: number; quality: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧫 AI Synthetic Data</h3>
    <div className="text-sm">{active}/{generators} active · {samples.toLocaleString()} samples · {quality}% quality</div>
  </div>);
}
