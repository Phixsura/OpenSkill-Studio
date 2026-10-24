"use client";
export function FleetAiStructPanel({ services, active, generations, validationRate }: { services: number; active: number; generations: number; validationRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 AI Structured Output</h3>
    <div className="text-sm">{active}/{services} active · {generations.toLocaleString()} gens · {validationRate}% valid</div>
  </div>);
}
