"use client";
export function FleetAiCompressPanel({ pipelines, active, models, reduction, qualityLoss }: { pipelines: number; active: number; models: number; reduction: number; qualityLoss: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗜️ AI Model Compression</h3>
    <div className="text-sm">{active}/{pipelines} active · {models} compressed · {reduction}% smaller · {qualityLoss}% loss</div>
  </div>);
}
