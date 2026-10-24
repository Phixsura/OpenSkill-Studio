"use client";
export function FleetArchFitnessV9Panel({ total, passing }: { total: number; passing: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏗️ Arch Fitness v9</h3>
    <div className="text-sm">{total} functions · {passing} passing</div>
  </div>);
}
