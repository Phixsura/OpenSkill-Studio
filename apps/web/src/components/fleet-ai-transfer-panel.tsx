"use client";
export function FleetAiTransferPanel({ jobs, active, baseModels, adaptations, improvement }: { jobs: number; active: number; baseModels: number; adaptations: number; improvement: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 AI Transfer Learning</h3>
    <div className="text-sm">{active}/{jobs} active · {baseModels} base models · {adaptations} adapted · +{improvement}% avg</div>
  </div>);
}
