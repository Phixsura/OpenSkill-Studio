"use client";

interface CompositeSlaCardProps { compositeSla: number; dependencies: number;
  weakest: string; weakestSla: number; downtimeMin: number; }

export function CompositeSlaCard({ compositeSla, dependencies, weakest, weakestSla, downtimeMin }: CompositeSlaCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 text-center border-b dark:border-gray-700">
        <div className="text-3xl font-bold text-blue-600">{compositeSla}%</div>
        <div className="text-xs text-gray-400">Composite SLA · {dependencies} dependencies</div>
        <div className="text-[10px] text-gray-400 mt-0.5">{downtimeMin}min allowed downtime/month</div>
      </div>
      <div className="p-3 text-xs text-center text-gray-500">
        Weakest: <span className="font-medium text-yellow-600">{weakest}</span> ({weakestSla}%)
      </div>
    </div>
  );
}
