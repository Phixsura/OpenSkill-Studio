"use client";
export function FleetAiOnboardV7Panel({ systems, active, completions, ttfv, drop }: { systems: number; active: number; completions: number; ttfv: number; drop: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 AI Onboarding v7</h3>
    <div className="text-sm">{active}/{systems} active · {completions.toLocaleString()} completions · TTFV {ttfv}m · {drop}% drop</div>
  </div>);
}
