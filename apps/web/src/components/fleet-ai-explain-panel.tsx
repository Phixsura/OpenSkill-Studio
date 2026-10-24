"use client";
export function FleetAiExplainPanel({ services, active, explanations, models }: { services: number; active: number; explanations: number; models: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 AI Explainability</h3>
    <div className="text-sm">{active}/{services} active · {explanations.toLocaleString()} explanations · {models} models</div>
  </div>);
}
