"use client";
export function FleetAiDataCurPanel({ curators, active, datasets, samples, quality }: { curators: number; active: number; datasets: number; samples: number; quality: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 AI Dataset Curator</h3>
    <div className="text-sm">{active}/{curators} active · {datasets} datasets · {samples.toLocaleString()} samples · {quality}% quality</div>
  </div>);
}
