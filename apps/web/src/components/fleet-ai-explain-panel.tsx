"use client";
export function FleetAiExplainPanel({ engines, active, explanations, methods, coverage }: { engines: number; active: number; explanations: number; methods: string[]; coverage: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 AI Explainability</h3>
    <div className="text-sm">{active}/{engines} active · {explanations.toLocaleString()} explanations · {methods.join(", ")} · {coverage}% coverage</div>
  </div>);
}
