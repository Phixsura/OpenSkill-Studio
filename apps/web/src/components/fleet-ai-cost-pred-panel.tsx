"use client";
export function FleetAiCostPredPanel({ predictors, active, predictions, accuracy, savings }: { predictors: number; active: number; predictions: number; accuracy: number; savings: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI Cost Predictor</h3>
    <div className="text-sm">{active}/{predictors} active · {predictions} predictions · {accuracy}% acc · ${savings.toLocaleString()} savings</div>
  </div>);
}
