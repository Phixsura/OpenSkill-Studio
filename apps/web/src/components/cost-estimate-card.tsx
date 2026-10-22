"use client";

interface CostEstimateCardProps { monthlyCost: number; dailyExecutions: number; perExecution: number; tier: string; }

export function CostEstimateCard({ monthlyCost, dailyExecutions, perExecution, tier }: CostEstimateCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="mb-2 font-semibold">💰 Cost Estimate</h4>
      <p className="text-2xl font-bold">${monthlyCost.toFixed(2)}<span className="text-sm text-gray-500">/month</span></p>
      <div className="mt-2 space-y-1 text-sm text-gray-500">
        <p>{dailyExecutions} executions/day × ${perExecution.toFixed(6)}/exec</p>
        <p>Tier: <span className="capitalize font-medium">{tier}</span></p>
      </div>
    </div>
  );
}
