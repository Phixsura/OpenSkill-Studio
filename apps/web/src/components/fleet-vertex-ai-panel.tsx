"use client";
export function FleetVertexAiPanel({ endpoints, deployed, models, predictions }: { endpoints: number; deployed: number; models: number; predictions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧠 Vertex AI</h3>
    <div className="text-sm">{deployed}/{endpoints} deployed · {models} models · {predictions.toLocaleString()} predictions</div>
  </div>);
}
