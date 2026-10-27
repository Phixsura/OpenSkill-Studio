"use client";

interface BillItem { metric: string; quantity: number; unitPrice: number; total: number; }
interface Bill { items: BillItem[]; totalCents: number; }

const metricIcons: Record<string, string> = { api_calls: "📡", compute_minutes: "⚡", storage_mb: "💾", bandwidth_gb: "🌐" };

export function UsageBillingCard({ bill }: { bill: Bill }) {
  if (!bill.items.length) return <div className="text-center text-gray-400 py-6 text-sm">No usage this period</div>;
  return (
    <div className="border dark:border-gray-700 rounded-xl overflow-hidden">
      <div className="p-4 bg-gray-50 dark:bg-gray-800">
        <span className="font-bold text-sm">Usage Bill</span>
        <span className="text-2xl font-extrabold block mt-1">${(bill.totalCents / 100).toFixed(2)}</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {bill.items.map(item => (
          <div key={item.metric} className="p-3 flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <span>{metricIcons[item.metric] || "📊"}</span>
              <div>
                <span className="font-medium capitalize">{item.metric.replace(/_/g, " ")}</span>
                <span className="text-xs text-gray-500 block">{item.quantity} × ${(item.unitPrice / 100).toFixed(3)}/unit</span>
              </div>
            </div>
            <span className="font-medium">${(item.total / 100).toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
