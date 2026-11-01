"use client";

interface RetentionCardProps { totalInstalls: number; retained: number; churned: number; retentionRate: number; }

export function RetentionCard({ totalInstalls, retained, churned, retentionRate }: RetentionCardProps) {
  const color = retentionRate >= 90 ? "green" : retentionRate >= 70 ? "yellow" : "red";
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="mb-2 font-semibold">📊 Retention</h4>
      <p className={`text-3xl font-bold text-${color}-600`}>{retentionRate}%</p>
      <div className="mt-2 grid grid-cols-3 gap-2 text-center text-sm">
        <div><p className="font-bold">{totalInstalls}</p><p className="text-xs text-gray-500">Total</p></div>
        <div><p className="font-bold text-green-600">{retained}</p><p className="text-xs text-gray-500">Retained</p></div>
        <div><p className="font-bold text-red-600">{churned}</p><p className="text-xs text-gray-500">Churned</p></div>
      </div>
    </div>
  );
}
