"use client";
export function FleetAiModelCompPanel({ checkers, active, models, passed, failed, frameworks }: { checkers: number; active: number; models: number; passed: number; failed: number; frameworks: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 AI Model Compliance</h3>
    <div className="text-sm">{active}/{checkers} active · ✅{passed} · ❌{failed} of {models} · {frameworks} frameworks</div>
  </div>);
}
