"use client";
export function FleetBicepPanel({ total, succeeded, failed }: { total: number; succeeded: number; failed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💪 Azure Bicep</h3>
    <div className="text-sm">{succeeded}✅ {failed}❌ of {total}</div>
  </div>);
}
