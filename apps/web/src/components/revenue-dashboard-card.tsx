"use client";

interface RevenueDashboardCardProps {
  mrr: string; arr: string; arpu: string; customers: number;
  growthPct: number; growthDirection: "up" | "down" | "flat";
}

export function RevenueDashboardCard({ mrr, arr, arpu, customers, growthPct, growthDirection }: RevenueDashboardCardProps) {
  const dirConfig = { up: { icon: "📈", color: "text-green-600" }, down: { icon: "📉", color: "text-red-600" }, flat: { icon: "➡️", color: "text-gray-500" } };
  const dir = dirConfig[growthDirection];

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Revenue</h3>
      <div className="mt-3 grid grid-cols-2 gap-4">
        <div>
          <p className="text-2xl font-bold">{mrr}</p>
          <p className="text-xs text-gray-400">MRR</p>
        </div>
        <div>
          <p className="text-2xl font-bold">{arr}</p>
          <p className="text-xs text-gray-400">ARR</p>
        </div>
        <div>
          <p className="text-lg font-semibold">{arpu}</p>
          <p className="text-xs text-gray-400">ARPU</p>
        </div>
        <div>
          <p className="text-lg font-semibold">{customers}</p>
          <p className="text-xs text-gray-400">Customers</p>
        </div>
      </div>
      <div className={`mt-3 text-sm ${dir.color}`}>{dir.icon} {growthPct}% vs last month</div>
    </div>
  );
}
