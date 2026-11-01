"use client";
export function FleetAiModelHlthPanel({ checkers, active, models, healthy, degraded, score }: { checkers: number; active: number; models: number; healthy: number; degraded: number; score: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💚 AI Model Health</h3>
    <div className="text-sm">{active}/{checkers} active · 🟢 {healthy} · 🟡 {degraded} of {models} · score {score}</div>
  </div>);
}
