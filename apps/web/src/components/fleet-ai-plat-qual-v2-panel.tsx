"use client";
export function FleetAiPlatQualV2Panel({ monitors, active, coverage, bugs, debt }: { monitors: number; active: number; coverage: number; bugs: number; debt: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✅ AI Quality v2</h3>
    <div className="text-sm">{active}/{monitors} active · {coverage}% coverage · {bugs} bugs · {debt}h debt</div>
  </div>);
}
