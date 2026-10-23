"use client";

interface LineItem { name: string; category: string; quantity: number; unit: string; unit_price: number; total: number; }
interface CostBreakdownChartProps { lineItems: LineItem[]; total: number;
  byCategory: Record<string, number>; largestCategory: string | null; }

const catColors: Record<string, string> = {
  compute: "bg-blue-500", storage: "bg-green-500", network: "bg-purple-500",
  database: "bg-orange-500", other: "bg-gray-500",
};

export function CostBreakdownChart({ lineItems, total, byCategory, largestCategory }: CostBreakdownChartProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Cost Breakdown</h2>
        <span className="text-xl font-bold">${total.toFixed(2)}</span>
      </div>
      <div className="flex h-4 overflow-hidden rounded-full">
        {Object.entries(byCategory).map(([cat, cost]) => (
          <div key={cat} className={`${catColors[cat] ?? catColors.other}`}
            style={{ width: `${(cost / Math.max(total, 0.01)) * 100}%` }}
            title={`${cat}: $${cost.toFixed(2)}`} />
        ))}
      </div>
      <div className="flex flex-wrap gap-3">
        {Object.entries(byCategory).map(([cat, cost]) => (
          <div key={cat} className="flex items-center gap-1.5 text-xs">
            <div className={`h-2.5 w-2.5 rounded-full ${catColors[cat] ?? catColors.other}`} />
            <span className="capitalize">{cat}</span>
            <span className="text-gray-400">${cost.toFixed(2)}</span>
          </div>
        ))}
      </div>
      <div className="space-y-1">
        {lineItems.map(item => (
          <div key={item.name} className="flex items-center justify-between text-sm">
            <span>{item.name}</span>
            <span className="text-gray-400">
              {item.quantity.toLocaleString()} {item.unit} × ${item.unit_price} = <strong>${item.total.toFixed(2)}</strong>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
