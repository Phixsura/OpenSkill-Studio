"use client";

interface CostLineItem {
  category: string;
  projected_usage: number;
  included: number;
  overage: number;
  unit_price: number;
  cost: number;
}

interface CostEstimateData {
  app_id: string;
  line_items: CostLineItem[];
  total_cost: number;
  budget_limit: number | null;
  over_budget: boolean;
  savings_vs_next_tier: number | null;
}

interface CostEstimateCardProps {
  estimate: CostEstimateData;
  appName: string;
}

const CAT_LABELS: Record<string, { label: string; icon: string }> = {
  api_calls: { label: "API Calls", icon: "📡" },
  bandwidth: { label: "Bandwidth", icon: "📶" },
  storage: { label: "Storage", icon: "💾" },
  compute: { label: "Compute", icon: "⚡" },
  webhooks: { label: "Webhooks", icon: "🔔" },
};

function formatCost(v: number): string {
  return v < 0.01 && v > 0 ? "<$0.01" : `$${v.toFixed(2)}`;
}

function formatUsage(v: number): string {
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `${(v / 1_000).toFixed(1)}K`;
  return v.toFixed(0);
}

export function CostEstimateCard({ estimate, appName }: CostEstimateCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div>
          <h3 className="font-semibold">Cost Estimate</h3>
          <p className="text-xs text-gray-500">{appName} • projected monthly</p>
        </div>
        <p className={`text-xl font-bold ${estimate.over_budget ? "text-red-600" : ""}`}>
          {formatCost(estimate.total_cost)}
        </p>
      </div>

      {estimate.over_budget && estimate.budget_limit !== null && (
        <div className="bg-red-50 px-4 py-2 text-xs font-medium text-red-700 dark:bg-red-900/10 dark:text-red-400">
          🚨 Over budget — limit {formatCost(estimate.budget_limit)}
        </div>
      )}

      {estimate.savings_vs_next_tier !== null && estimate.savings_vs_next_tier > 0 && (
        <div className="bg-blue-50 px-4 py-2 text-xs text-blue-700 dark:bg-blue-900/10 dark:text-blue-400">
          💡 Save {formatCost(estimate.savings_vs_next_tier)}/mo by upgrading to Growth tier
        </div>
      )}

      <div className="divide-y divide-gray-100 dark:divide-gray-800">
        {estimate.line_items.map((li) => {
          const cat = CAT_LABELS[li.category] ?? { label: li.category, icon: "📊" };
          return (
            <div key={li.category} className="flex items-center justify-between px-4 py-2.5">
              <div className="flex items-center gap-2">
                <span>{cat.icon}</span>
                <div>
                  <p className="text-xs font-medium">{cat.label}</p>
                  <p className="text-[10px] text-gray-400">
                    {formatUsage(li.projected_usage)} projected • {formatUsage(li.included)}{" "}
                    included
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className={`text-sm font-medium ${li.cost > 0 ? "" : "text-gray-400"}`}>
                  {formatCost(li.cost)}
                </p>
                {li.overage > 0 && (
                  <p className="text-[10px] text-orange-600">{formatUsage(li.overage)} overage</p>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {estimate.line_items.length === 0 && (
        <div className="py-6 text-center text-sm text-gray-500">No usage data yet</div>
      )}
    </div>
  );
}
