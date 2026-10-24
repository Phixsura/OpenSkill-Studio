"use client";
export function FleetAiInputSanPanel({ sanitizers, active, sanitized, threats, rules }: { sanitizers: number; active: number; sanitized: number; threats: number; rules: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧹 AI Input Sanitizer</h3>
    <div className="text-sm">{active}/{sanitizers} active · {sanitized.toLocaleString()} sanitized · {threats.toLocaleString()} threats · {rules} rules</div>
  </div>);
}
