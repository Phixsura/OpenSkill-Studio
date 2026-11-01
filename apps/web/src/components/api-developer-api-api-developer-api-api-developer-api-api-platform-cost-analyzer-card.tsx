"use client";

interface ItemInfo { dimension: string; cost_cents: number; usage: number; unit: string; }
interface Props { period: string; items: ItemInfo[]; totalCents: number; totalSpendCents: number; appName: string; }

function fmtCost(c: number) { return `$${(c / 100).toFixed(2)}`; }
const dIcon: Record<string, string> = { compute: "⚙️", storage: "💾", bandwidth: "🌐", api_calls: "📡", webhooks: "🪝" };

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiPlatformCostAnalyzerCard({ period, items, totalCents, totalSpendCents, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💰 Cost Analyzer</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {period}</p>
        </div>
        <div className="text-right">
          <span className="text-sm font-bold text-green-600">{fmtCost(totalCents)}</span>
          <p className="text-[9px] text-gray-400">all-time: {fmtCost(totalSpendCents)}</p>
        </div>
      </div>
      {items.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No cost data</p>
      ) : (
        <div className="space-y-1.5">
          {items.map((i) => (
            <div key={i.dimension} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{dIcon[i.dimension] ?? "•"} {i.dimension}</span>
              <span className="text-gray-400">{fmtCost(i.cost_cents)} · {i.usage.toLocaleString()} {i.unit}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
