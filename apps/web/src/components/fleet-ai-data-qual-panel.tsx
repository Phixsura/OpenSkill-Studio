"use client";
export function FleetAiDataQualPanel({ monitors, active, datasets, checks, quality }: { monitors: number; active: number; datasets: number; checks: number; quality: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✅ AI Data Quality</h3>
    <div className="text-sm">{active}/{monitors} active · {datasets} datasets · {checks.toLocaleString()} checks · {quality}% quality</div>
  </div>);
}
