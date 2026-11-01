"use client";
export function FleetAiExplainV2Panel({ explainers, active, explanations, methods, satisfaction }: { explainers: number; active: number; explanations: number; methods: number; satisfaction: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 AI Explainer v2</h3>
    <div className="text-sm">{active}/{explainers} active · {explanations.toLocaleString()} explanations · {methods} methods · {satisfaction}% satisfaction</div>
  </div>);
}
