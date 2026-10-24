"use client";
export function FleetAiRlV4Panel({ limiters, active, rules, throttled, adaptive }: { limiters: number; active: number; rules: number; throttled: number; adaptive: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚦 AI Rate Limiter v4</h3>
    <div className="text-sm">{active}/{limiters} active · {rules} rules · {throttled.toLocaleString()} throttled · {adaptive ? "✅ adaptive" : "⚪"}</div>
  </div>);
}
