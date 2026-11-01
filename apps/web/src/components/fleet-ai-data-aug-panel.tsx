"use client";
export function FleetAiDataAugPanel({ pipelines, active, samples, multiplier, techniques }: { pipelines: number; active: number; samples: number; multiplier: number; techniques: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 AI Data Augmentation</h3>
    <div className="text-sm">{active}/{pipelines} active · {samples.toLocaleString()} samples · {multiplier}x · {techniques} techniques</div>
  </div>);
}
