"use client";
export function FleetAiQualityV7Panel({ monitors, active, coverage, debt, bugs, smells }: { monitors: number; active: number; coverage: number; debt: number; bugs: number; smells: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✅ AI Quality v7</h3>
    <div className="text-sm">{active}/{monitors} active · {coverage}% coverage · {debt}h debt · {bugs} bugs · {smells} smells</div>
  </div>);
}
