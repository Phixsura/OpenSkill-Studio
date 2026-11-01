"use client";
export function FleetAiEvalDataPanel({ managers, active, datasets, samples, domains }: { managers: number; active: number; datasets: number; samples: number; domains: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Eval Dataset</h3>
    <div className="text-sm">{active}/{managers} active · {datasets} datasets · {samples.toLocaleString()} samples · {domains} domains</div>
  </div>);
}
