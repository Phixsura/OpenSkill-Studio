"use client";
export function FleetFeatAdoptPanel({ total, widelyAdopted, avgAdoption, good }: { total: number; widelyAdopted: number; avgAdoption: number; good: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 Feature Adoption</h3>
    <div className={`text-lg font-bold ${good ? "text-green-600" : "text-yellow-600"}`}>{avgAdoption}%</div>
    <div className="text-xs text-gray-400">{widelyAdopted}/{total} widely adopted</div>
  </div>);
}
